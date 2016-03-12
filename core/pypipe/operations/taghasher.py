"""
Finite tags vectoriser module
@starcolon projects
"""


import numpy as np
import os.path
import pickle
import json
from termcolor import colored
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD

def new():
	vectorizer = CountVectorizer(
		encoding='utf-8',
		ngram_range=(1,1),
		max_features=128,
		binary=True
	)
	
	return vectorizer


def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path):
	if os.path.isfile(path): return load(path)
	else: return new()

def hash(operations,learn=False):
	pass #TAOTODO: