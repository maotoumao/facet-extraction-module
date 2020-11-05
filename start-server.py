from flask import Flask, request, jsonify, send_file
import json
import os
import zipfile
from flask_cors import cross_origin
from concurrent.futures import ThreadPoolExecutor
from gevent import pywsgi

import preprocess.getCentralWord as GetCentralWord
import preprocess.getSummaryEmbedding as GetSummaryEmbedding
import preprocess.getTopicHieraries as GetTopicHieraries

import tofm.generateP as GenerateP
import tofm.topicCluster as TopicCluster
import tofm.generateF as GenerateF
import tofm.lp as LP
import tofm.analyse as Analyse

app = Flask(__name__)
executor =ThreadPoolExecutor(2)

def loadConfig():
    with open('./config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def createDir(outputBasePath, domain, topicList):
    _topicList = topicList[:]
    _topicList.append('__tmpData')
    for topic in _topicList:
        if not os.path.exists(os.path.join(outputBasePath,  domain,  topic)):
            os.makedirs(os.path.join(
                outputBasePath,  domain,  topic))


config = loadConfig()
status = {}


def getStatus(domain, topicList, outputBasePath):
    if domain == None or topicList == None:
        return {
            'status': 'ILLEGAL_CLASSNAME'
        }
    if topicList == None:
        topicList = []
    if domain in status:
        return {
            'status': 'CONSTRUCTING',
            'meta': status[domain]
        }
    elif(not os.path.exists(os.path.join(outputBasePath, domain))):
        return {
            'status': 'NOT_EXIST'
        }
    statusList = [os.path.exists(os.path.join(outputBasePath, domain, t)) for t in topicList]
    if all(statusList):
        return {
            'status': 'EXIST'
        }
    return {
        'status': 'NOT_COMPLETE'
    }

def preprocess(domain, topicList):
    createDir(config['outputBasePath'], domain, topicList)
    status[domain]['step'] = 'PREPROCESS_ANALYSE_INIT_FACETS'
    GetCentralWord.run(domain, topicList, config['rawDataPath'], config['outputBasePath'])
    status[domain]['step'] = 'PREPROCESS_ANALYSE_SUMMARY_EMBEDDING'
    GetSummaryEmbedding.run(domain, topicList, config['rawDataPath'], config['outputBasePath'])
    status[domain]['step'] = 'PREPROCESS_ANALYSE_TOPIC_HIERARY'
    GetTopicHieraries.run(domain, topicList, config['rawDataPath'], config['outputBasePath'])

def toFM(domain, topicList):
    status[domain]['step'] = 'ALG_CALCULATE_SIMILARITIES'
    GenerateP.run(domain, topicList, config['outputBasePath'])
    status[domain]['step'] = 'ALG_TOPIC_CLUSTERING'
    TopicCluster.run(domain, topicList, config['outputBasePath'])
    status[domain]['step'] = 'ALG_GENERATE_PROPAGATION_MATRIX'
    GenerateF.run(domain, topicList, config['outputBasePath'])
    status[domain]['step'] = 'ALG_LABEL_PROPAGATION'
    LP.run(domain, config['outputBasePath'])
    status[domain]['step'] = 'ALG_ANALYSE_FACET_SET'
    Analyse.run(domain, config['outputBasePath'])
    status.pop(domain)

def algorithmTask(domain, topicList):
    preprocess(domain, topicList)
    toFM(domain, topicList)

def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

app.after_request(after_request)

@app.route('/facet-extract', methods=['POST'])
@cross_origin()
def facetExtract():
    if request.method == 'POST':
        domain = request.get_json().get('className')
        topicList = request.get_json().get('topicNames')
        status[domain] = {
            'step': 'READY'
        }
        executor.submit(algorithmTask, domain, topicList)
        return jsonify({'status': 'CONSTRUCTING'})


@app.route('/facet-extract-status', methods=['POST'])
@cross_origin()
def facetExtractStatus():
    if request.method == 'POST':
        domain = request.get_json().get('className')
        topicList = request.get_json().get('topicNames')
        constructStatus = getStatus(domain, topicList, config['outputBasePath'])
        return jsonify(constructStatus)

# @app.route('/download-init-facets', methods=['POST'])
# @cross_origin()
# def downloadInitFacets():
#     return

@app.route('/download-facet-set', methods=['POST'])
@cross_origin()
def downloadFacets():
    if request.method == 'POST':
        domain = request.get_json().get('className')
        topicList = request.get_json().get('topicNames')
        if getStatus(domain, topicList, config['outputBasePath'])['status'] == 'EXIST':
            _zipFile = zipfile.ZipFile(os.path.join(config['outputBasePath'], domain, '__tmpData', domain + '_facetSets.zip'), 'w')
            for topic in topicList:
                _zipFile.write(os.path.join(config['outputBasePath'], domain, topic, 'facetSet.txt'), arcname=topic+'.txt')
            _zipFile.close()
            return send_file(os.path.join(config['outputBasePath'], domain, '__tmpData', domain + '_facetSets.zip'), as_attachment=True)
        return jsonify({
            'status': 'NOT_CONSTRUCTED'
        }), 404

@app.route('/get-init-facets', methods=['POST'])
@cross_origin()
def getInitFacets():
    if request.method == 'POST':
        domain = request.get_json().get('className')
        topicList = request.get_json().get('topicNames')
        stat = getStatus(domain, topicList, config['outputBasePath'])
        if stat['status'] == 'EXIST' or (stat['status'] == 'CONSTRUCTING' and stat['meta']['step'].startswith('ALG_')):
            result = {}
            for topic in topicList:
                with open(os.path.join(config['outputBasePath'], domain, topic, 'centralWord.txt'), 'r', encoding='utf-8') as f:
                    result[topic] = [fa.strip() for fa in f.readlines()]
            return jsonify(result)
        return jsonify({'status': 'NOT_FOUND'}), 404


@app.route('/get-facet-set', methods=['POST'])
@cross_origin()
def getFacetSet():
    if request.method == 'POST':
        domain = request.get_json().get('className')
        topicList = request.get_json().get('topicNames')
        if getStatus(domain, topicList, config['outputBasePath'])['status'] == 'EXIST':
            result = {}
            for topic in topicList:
                with open(os.path.join(config['outputBasePath'], domain, topic, 'facetSet.txt'), 'r', encoding='utf-8') as f:
                    result[topic] = [fa.strip() for fa in f.readlines()]
                    result[topic].sort()
            return jsonify(result)
        return jsonify({'status': 'NOT_FOUND'}), 404

if __name__ == '__main__':
    # server = pywsgi.WSGIServer(('0.0.0.0', 4675), app)
    # server.serve_forever()
    app.run(host='0.0.0.0', port='4675')