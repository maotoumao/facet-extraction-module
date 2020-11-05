import re
import os
from bert_serving.client import BertClient
import numpy as np

bc = BertClient(check_length=False)

def removeNullContent(content):
    return re.sub('(?:\\(.*\\))|(?:\\[.*\\])', '', content)

def getSummaryEmbedding(domain, topicList, rawDataPath, outputBasePath):
    summaries = []
    topics = []
    for topic in topicList:
        topic = topic.strip()
        if os.path.exists(os.path.join(outputBasePath, domain, topic, 'summaryEmbedding.txt')):
            continue
        with open(os.path.join(rawDataPath, domain, topic, 'summary.txt'), 'r', encoding='utf-8') as f:
            summary = removeNullContent(''.join(f.readlines())).strip()
            if len(summary) == 0:
                summary = 'this is a null topic'
            summaries.append(summary)
        topics.append(topic)
    if(len(summaries) > 0):
        embeddings = bc.encode(summaries)
    
    for i in range(len(topics)):
        print(i/ len(topics))
        np.savetxt(os.path.join(outputBasePath, domain, topics[i], 'summaryEmbedding.txt'), embeddings[i])   

def run(domain, topicList, rawDataPath, outputBasePath):
    getSummaryEmbedding(domain, topicList, rawDataPath, outputBasePath)
