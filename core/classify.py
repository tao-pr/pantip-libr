"""
Topic classifier module
@starcolon projects
"""

import os
import sys
import json
import argparse
import numpy as np
from termcolor import colored
from pypipe import pipe as Pipe
from pypipe import datapipe as DP
from pypipe.operations import rabbit
from pypipe.operations import tapper as T
from pypipe.operations import cluster
from pypipe.operations import taghasher
from pypipe.operations import texthasher
from pypipe.operations import textcluster


class Classifier:

  REPO_DIR = os.getenv('PANTIPLIBR','../..')
  TEXT_VECTORIZER_PATH  = '{0}/data/models/vectoriser'.format(REPO_DIR)
  TAG_HASHER_PATH       = '{0}/data/models/taghash'.format(REPO_DIR)
  CLF_PATH              = '{0}/data/models/clf'.format(REPO_DIR)
  STOPWORDS_PATH        = '{0}/data/words/stopwords.txt'.format(REPO_DIR)
  CSV_REPORT_PATH       = '{0}/data/report.csv'.format(REPO_DIR)


  def __init__(self):
    # Load the trained models
    self.topicHasher = texthasher.safe_load(TEXT_VECTORIZER_PATH,stop_words=[])
    self.tagHasher   = taghasher.safe_load(TAG_HASHER_PATH,n_feature=256)
    self.contentClf  = textcluster.safe_load(CONTENT_CLUSTER_PATH,n_labels=16)
    self.clf         = cluster.safe_load(CLF_PATH)

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
    pass
