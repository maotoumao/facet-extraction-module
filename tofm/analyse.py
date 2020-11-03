# -*- coding: utf-8 -*-
import os
import json
import numpy as np


def getOriginFacetNums(domain, topic, outputBasePath):
    with open(os.path.join(outputBasePath, domain, topic, 'centralWord.txt'), 'r', encoding='utf-8') as f:
        return len(f.readlines())


def get_part_dict(domain, outputBasePath):
    with open(os.path.join(outputBasePath, domain, '__tmpData', 'partDict.json'), 'r', encoding='utf-8') as f:
        part_dict = json.load(f)
    return part_dict


def analyse(domain, outputBasePath):
    with open(os.path.join(outputBasePath, domain, '__tmpData', 'allFacets.txt'), 'r', encoding='utf-8') as f:
        af = f.readlines()
        af = [a.strip() for a in af]

    part_dict = get_part_dict(domain, outputBasePath)
    # 在每一个簇内进行分析， index是簇标号
    for index in part_dict.keys():
        result = np.loadtxt(os.path.join(outputBasePath, domain, '__tmpData', 'result_chunk_'+str(index)+'.txt'))
        topicList=part_dict[index]
        for topicIndex in range(len(topicList)):
            facets = ['application', 'property', 'example', 'definition']
            tf=result[topicIndex]
            facetNums=getOriginFacetNums(
                domain, topicList[topicIndex], outputBasePath) * 1.5
            facetNums=6 if facetNums < 6 else facetNums
            for i in range(int(facetNums)):
                maxPos = np.where(tf == np.max(tf))
                y = maxPos[0][0]
                targetFacet = af[y]
                tf[y] = 0
                facets.append(targetFacet)
            facets = [fa + '\n' for fa in facets]
            facets = list(set(facets))
            with open(os.path.join(outputBasePath, domain, topicList[topicIndex], 'facetSet.txt'), 'w', encoding='utf-8') as f:
                f.writelines(facets)

def run(domain, outputBasePath):
    analyse(domain, outputBasePath)



