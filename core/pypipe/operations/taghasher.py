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
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import MaxAbsScaler
from sklearn.decomposition import NMF

def new(n_feature=128):
	vectorizer = CountVectorizer(
		encoding='utf-8',
		ngram_range=(1,1), # Unigram only
		max_features=n_feature,	
		binary=True
	)

	smoother = NMF(n_components=n_feature)

	# Scaler which scales the feature values by abs max
	scaler = MaxAbsScaler(copy=True) #Avoid in-place update

	return [vectorizer,smoother,scaler]


def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path,n_feature):
	if os.path.isfile(path): return load(path)
	else: return new(n_feature)

def hash(operations,learn=False):
	def _hashMe(dataset):
		x= dataset

		if learn:
			for i in range(len(operations)):
				print('Processing #{0} : {1}'.format(i,type(operations[i])))
				x = operations[i].fit_transform(x)
		else:
			for i in range(len(operations)): 
				x = operations[i].transform(x)

		return iter(x)
	return _hashMe
