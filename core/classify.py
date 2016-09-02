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

  def __init__(self):
    # TAOTODO: Load models
    pass

  def classify(self,topic):
    pass

  def create_topic(self,title,tags,content):
    pass
