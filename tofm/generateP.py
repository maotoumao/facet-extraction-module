# -*-coding:utf-8 -*-
import os
import numpy as np


def calCos(x, y):
    num = x.dot(y.T)
    denom = np.linalg.norm(x) * np.linalg.norm(y)
    return num / denom


def generateP(domain, topicList, outputBasePath):
    topicNums = len(topicList)
    p = np.eye(topicNums)
    for i in range(topicNums):
        for j in range(i+1, topicNums):
            sim = calCos(np.loadtxt(os.path.join(outputBasePath, domain, topicList[i], 'summaryEmbedding.txt')), np.loadtxt(
                os.path.join(outputBasePath, domain, topicList[j], 'summaryEmbedding.txt')))
            p[i, j] = sim
            p[j, i] = sim
        print('percent:', i/topicNums)
    p_normed = (p-p.min())/(1-p.min())
    np.savetxt(os.path.join(outputBasePath, domain, '__tmpData', 'p.txt'), p_normed)


def run(domain, topicList, outputBasePath):
    generateP(domain, topicList, outputBasePath)