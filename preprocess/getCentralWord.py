# -*- coding:utf-8 -*-
import os
import nltk


stop_save_words = ["see also", "references", "external links",
                   "further reading", "vs.", "citations", 'notes']
useless_words = ["overview", "bibliography",
                 "other", "case", "class", "summary", 'papers']

lmztr = nltk.stem.wordnet.WordNetLemmatizer()


def change_bad_word(word):
    word = word.lower()
    if (word.find("advantage") != -1):
        return "property"
    if (word.find("performance") != -1):
        return "property"
    if (word.find("efficiency") != -1):
        return "property"
    if (word.find("characterization") != -1):
        return "property"
    if (word.find("analysis") != -1):
        return "property"
    if (word.find("comparison") != -1):
        return "property"
    if (word.find("implemantation") != -1):
        return "implementation"
    if (word.find("implemantations") != -1):
        return "implementation"
    if (word.find("language support") != -1):
        return "implementation"
    if (word.find("pseudocode") != -1):
        return "implementation"
    if (word.find("usage") != -1):
        return "application"
    if (word.find("using") != -1):
        return "application"
    if (word.find("use") != -1):
        return "application"
    if (word.find("description") != -1):
        return "definition"
    if (word.find("algorithm") != -1):
        return "method"
    if (word.strip() == "concept"):
        return "definition"
    return word


def useless_filter_list(facetList):
    remove_list = []
    for facet in facetList:
        for w in stop_save_words:
            if(facet.lower().find(w) != -1):
                remove_list.append(facet)
        for w in useless_words:
            if(facet.lower().find(w) != -1):
                remove_list.append(facet)
    remove_list = list(set(remove_list))
    for r in remove_list:
        facetList.remove(r)
    return facetList


# 变成小写单数

def normalize(lmtzr, facetList):
    newList = []
    for facet in facetList:
        facet = facet.lower().strip()
        facet = ' '.join([lmtzr.lemmatize(w, pos='n')
                          for w in facet.split(' ')])
        newList.append(facet.strip() + '\n')

    return removeDump(newList)


def removeDump(facetList):
    # 去除空行
    facetList = [fl.strip() for fl in facetList if fl.strip() != '']
    # 去重
    facetList = list(set(facetList))
    facetList = [fl+'\n' for fl in facetList]
    return facetList


def get_central_word(domain, topicList, rawDataPath, outputBasePath):
    # preps = ["of", "for", "at", "in", "on", "over", "to", "by", "about", "under", "after"]
    for topic in topicList:
        # print('central_word:', topic)
        if os.path.exists(os.path.join(outputBasePath, domain, topic,
                                       'centralWord.txt')):
            continue
        topic = topic.strip()
        with open(os.path.join(rawDataPath, domain, topic, 'facets.txt'), 'r', encoding='utf-8') as f:
            facet_list = f.readlines()
            facet_list = useless_filter_list(facet_list)
            new_list = []
            for facet in facet_list:
                facet = facet.lower()
                # facet = ''.join(f for f in facet if f not in [':', ',', '(', ')'])
                tokens = nltk.word_tokenize(facet)
                if (len(tokens) == 1):
                    pos_tags = nltk.pos_tag(tokens)
                    if (pos_tags[0][1].startswith('NN') and (len(tokens[0]) > 1)):
                        new_list.append(change_bad_word(tokens[0]) + '\n')
                else:
                    central_facet = ''
                    pos_tags = nltk.pos_tag(tokens)
                    record = False
                    for word in pos_tags:
                        if word[1].startswith('JJ'):
                            record = True
                            continue
                        if (record and word[1] == 'IN'):
                            break

                        if (word[1].startswith('NN') and not record):
                            record = True

                        if (record and word[1] in [':', ',', '(', ')', '#']):
                            break

                        if (record):
                            # central_facet += (word[0] + ' ')
                            central_facet = word[0]  # 只提取一个中心词

                    if central_facet != '' and len(central_facet) > 1:
                        central_facet = central_facet.strip()
                        new_list.append(change_bad_word(central_facet) + '\n')
            new_list = normalize(lmztr, new_list)
            new_list.sort()
            file = open(os.path.join(outputBasePath, domain, topic,
                                     'centralWord.txt'), 'w', encoding='utf-8')
            file.writelines(new_list)
            file.close()


def run(domain, topicList, rawDataPath, outputBasePath):
    try:
        get_central_word(domain, topicList, rawDataPath, outputBasePath)
    except Exception as e:
        print(e)
    
