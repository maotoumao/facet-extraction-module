# -*- coding:utf-8 -*-
import os
import numpy as np
import community
import networkx as nx
import json
import csv


# 加载上下位关系
def load_sxw(domain, topicList, outputBasePath):
    sxw = open(os.path.join(outputBasePath, domain,
                            '__tmpData', 'sxw.csv'), 'r', encoding='utf-8')
    csv_reader = csv.reader(sxw)
    # 上下位关系是乱序的，所以需要从字典里查找
    sxw = []
    for row in csv_reader:
        sxw.append(row)
    return sxw


# 根据上下位生成网络图
def generate_graph(nodes, sxw):
    G = nx.Graph()
    for n in nodes:
        G.add_node(n)
    for j in range(len(sxw)):
        G.add_edge(sxw[j][0], sxw[j][1])
    return G


# 根据网络图进行louvain划分，返回结果是一个字典，字典的每一个value列表代表一个类
def get_partition(G):
    partition = community.best_partition(G)
    nodes = G.nodes()
    partDict = {}
    for node in nodes:
        if partition[node] in partDict:
            partDict[partition[node]].append(node)
        else:
            partDict[partition[node]] = [node]

    mergeDict = {-1: []}
    for k in partDict.keys():
        if len(partDict[k]) < 3:
            mergeDict[-1].extend(partDict[k])
        else:
            mergeDict[k] = partDict[k]
    
    return mergeDict


# 根据分割结果对P进行分割
def split_p(domain, topicList, part_dict, outputBasePath):
    ori_p = np.loadtxt(os.path.join(outputBasePath, domain, '__tmpData', 'p.txt'))
    for k in part_dict.keys():
        # 将主题结点提出作为子矩阵
        sub_topic_nums = len(part_dict[k])
        matrix = np.eye(sub_topic_nums)

        for i in range(sub_topic_nums):
            for j in range(i + 1, sub_topic_nums):
                # print(topicList.index(part_dict[k][i]), topicList.index(part_dict[k][j]), part_dict[k][i], part_dict[k][j])
                matrix[i][j] = ori_p[topicList.index(part_dict[k][i])][topicList.index(part_dict[k][j])]
                matrix[j][i] = matrix[i][j]
        # 簇的名字
        class_name = 'p_chunk_' + str(k) +'.txt'
        # 将新的P写入
        np.savetxt(os.path.join(outputBasePath, domain, '__tmpData', class_name), matrix)


# 写入社团划分结果
def write_part_dict(domain, part_dict, outputBasePath):
    with open(os.path.join(outputBasePath, domain, '__tmpData', 'partDict.json'), 'w', encoding='utf-8') as f:
        json.dump(part_dict, f)


def run(domain, topicList, outputBasePath):
    sxw = load_sxw(domain, topicList, outputBasePath)
    G = generate_graph(topicList, sxw)
    part_dict = get_partition(G)
    write_part_dict(domain, part_dict, outputBasePath)
    split_p(domain, topicList, part_dict, outputBasePath)
