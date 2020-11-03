import os
import csv
from nltk.stem.wordnet import WordNetLemmatizer


lm = WordNetLemmatizer()

# 函数
# 判断某个主题是否包含另一个主题 比如k-d_tree和Relaxed_k-d_tree 返回下标


def isPart(topic, topicList):
    i = 0
    for t in topicList:
        if t != topic:
            # 判断topic是否包含t
            if topic.find(t) != -1 and topic[topic.find(t) - 1] == ' ':
                return i
        i += 1
    return -1

# 从句子中寻找最大匹配的主题


def findMaxMatchTopic(sentence, topicList):
    index = -1
    currIndex = 0
    topic_length = 0
    for t in topicList:
        if (sentence.find(t) != -1):
            if (len(t) > topic_length):
                index = currIndex
                topic_length = len(t)
        currIndex += 1
    return index

# 根据category发现上下位关系
def findSxwFromCategory(rawDataPath, domain, topic, topicList, lm):
    indexes = []
    with open(os.path.join(rawDataPath, domain, topic, 'hierarchies.txt'), 'r', encoding='utf-8') as f:
        categories = f.readlines()
        categories = [c.strip().replace('(', '').replace(')', '').lower()
                              for c in categories]
        for c in categories:
            c = ' '.join([lm.lemmatize(w, pos='n') for w in c.split(' ')])
            index = 0
            for t in topicList:
                if t == c:
                    indexes.append(index)
                    break
                index += 1
    return indexes

# 寻找定义语句，从中发现上下位关系
def findSxwFromDefination(rawDataPath, domain, topic, topicList):
    with open(os.path.join(rawDataPath, domain, topic, 'summary.txt'), 'r', encoding='utf-8') as f:
        content=f.readline()
        topic=topic.lower().replace('_', ' ')
        sentences=content.split('.')
        for sentence in sentences:
            sentence=sentence.lower()
            if sentence.find(topic) != -1 and sentence.find('is') != -1:
                # 将is之后的内容截取
                candidate_content=sentence[sentence.find('is') + 2:]
                # 判断是否是单句
                if candidate_content.find(',') != -1:
                    candidate_content=candidate_content[:candidate_content.find(
                        ',')]
                # 从候选的内容中寻找主题
                index=findMaxMatchTopic(candidate_content, topicList)
                return index
    return -1


# 
def run(domain, topicList, rawDataPath, outputPath):
    normalizedTopicList=[t.lower().replace('(', '').replace(
        ')', '').replace('_', ' ') for t in topicList]
    sxw=[]

    # 遍历主题
    for topic in topicList:
        # 根据主题名称直接判断上下位
        index=isPart(topic.lower().replace('_', ' '), normalizedTopicList)
        if index != -1:
            sxw.append([topicList[index], topic])
        # 根据定义语句判断上下位
        index=findSxwFromDefination(rawDataPath, domain, topic, normalizedTopicList)
        if index != -1:
            sxw.append([topicList[index], topic])

        indexes=findSxwFromCategory(rawDataPath, domain, topic, normalizedTopicList, lm)
        for index in indexes:
            sxw.append([topicList[index], topic])
    
    with open(os.path.join(outputPath, domain, '__tmpData', 'sxw.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(sxw)