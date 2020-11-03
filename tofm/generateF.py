# -*- coding: utf-8 -*-
import json
import os
import numpy as np

def get_part_dict(domain, outputBasePath):
    with open(os.path.join(outputBasePath, domain, '__tmpData', 'partDict.json'), 'r', encoding='utf-8') as f:
        part_dict = json.load(f)
    return part_dict


def getFacetsCompleteSet(domain, topicList, outputBasePath):
    all_facets = []
    for topic in topicList:
        with open(os.path.join(outputBasePath, domain, topic, 'centralWord.txt'), 'r', encoding='utf-8') as f:
            all_facets.extend(f.readlines())
    all_facets = [a.strip() + '\n' for a in all_facets]
    all_facets = list(set(all_facets))
    with open(os.path.join(outputBasePath, domain, '__tmpData', 'allFacets.txt'), 'w', encoding='utf-8') as f:
        f.writelines(all_facets)
    return all_facets


def constructF(domain, topicList, outputBasePath):
    part_dict = get_part_dict(domain, outputBasePath)
 
    facet_list = getFacetsCompleteSet(domain, topicList, outputBasePath)
    facet_list = [f.strip() for f in facet_list]

    # 循环构建F
    for k in part_dict.keys():
        topic_list = part_dict[str(k)]
        class_name = 'f_chunk_' + str(k) + '.txt'
        # print('constructing ' + class_name)
        F = np.zeros([len(topic_list), len(facet_list)])

        for topic_index in range(len(topic_list)):
            with open(os.path.join(outputBasePath, domain, topic_list[topic_index], 'centralWord.txt'), 'r', encoding='utf-8') as f:
                flist = f.readlines()
                for fl in flist:
                    fl = fl.strip()
                    F[topic_index, facet_list.index(fl)] = 1

        np.savetxt(os.path.join(outputBasePath, domain, '__tmpData', class_name), F, fmt='%s')

def run(domain, topicList, outputBasePath):
    constructF(domain, topicList, outputBasePath)