"""
Topic classification server as a microservice
@starcolon projects
"""

import os
import sys
import json
import argparse
import numpy as np
from flask import Flask
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe import datapipe as DP
from pypipe.operations import rabbit
from pypipe.operations import tapper as T
from pypipe.operations import cluster
from pypipe.operations import taghasher
from pypipe.operations import texthasher
from pypipe.operations import textcluster

REPO_DIR = os.getenv('PANTIPLIBR','../..')
TEXT_VECTORIZER_PATH  = '{0}/data/models/vectoriser'.format(REPO_DIR)
TAG_HASHER_PATH       = '{0}/data/models/taghash'.format(REPO_DIR)
CLF_PATH              = '{0}/data/models/clf'.format(REPO_DIR)
STOPWORDS_PATH        = '{0}/data/words/stopwords.txt'.format(REPO_DIR)
CSV_REPORT_PATH       = '{0}/data/report.csv'.format(REPO_DIR)


class Classifier:

  def __init__(self):
    # Load the trained models
    self.topicHasher = texthasher.safe_load(TEXT_VECTORIZER_PATH,stop_words=[])
    self.tagHasher   = taghasher.safe_load(TAG_HASHER_PATH,n_feature=256)
    self.clf         = cluster.safe_load(CLF_PATH,method=None,n_features=256)

  def classify(self,topic):
    # Prepare processing functions
    hashMe     = texthasher.hash(topicHasher,learn=False)
    clusterMe  = textcluster.classify(contentClf,learn=False)
    hashtagMe  = taghasher.hash(tagHasher,learn=False)
    classifyMe = cluster.analyze(clf)

    v = hashMe(str(topic['title'] + topic['topic']))
    t = ' '.join([tag for tag in topic['tags'] if len(tag)>1])
    w = hashtagMe(t)
    x = list(v) + list(w)

    y = classifyMe(x)
    return y

  def create_topic(self,title,tags,content):
    return {
      'title': title,
      'tags' : tags,
      'topic': content
    }


# Server configuration and setup
app = Flask(__name__)

class ErrorResponse(Exception):
  status_code = 500

  def __init__(self,message,status_code=500):
    Exception.__init__(self)
    self.message     = message
    self.status_code = status_code


# Server lifetime-wide variables
clf         = Classifier()
ALL_ATTRS   = ['title','topic','tags']
INVALID_REQ = ErrorResponse('Invalid Request',500)

def try_parse(req):
  if len(req)<3:
    return None
  elif any([(attr not in req) for attr in ALL_ATTRS]):
    return None
  else:
    return req

def classify_req(topic):
  # TAOTODO: Log the request
  global clf
  c = clf.classify(topic)
  return c

@app.route('/')
def root():
  return __name__

@app.errorhandler(ErrorResponse)
def handle_http_error(e):
  return json.dumps(e)

@app.route('/classify', methods=['POST'])
def classify():
  # Parse the JSON request data
  req = try_parse(request.json)
  if req is None:
    # Invalid request package
    raise INVALID_REQ
  else:
    return classify_req(req)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=1996)



