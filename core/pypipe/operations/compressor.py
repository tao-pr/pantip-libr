"""
Vector compressor
@starcolon projects
"""

import numpy as np
import os.path
import pickle
import json
from termcolor import colored
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import TruncatedSVD


# Create a text process pipeline (vectorizer)
def new(n_components=None):

	# Prepare dimentionality reducer
	if n_components is None:
		svd = TruncatedSVD()
	else:
		svd = TruncatedSVD(n_components)

	# Prepare normaliser
	norm = Normalizer(norm='l2') # Cosine similarity 

	operations = [svd,norm]
	return operations


def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path,n_components):
	if os.path.isfile(path): return load(path)
	else: return new(n_components)

def compress(operations,learn=False):
	# @param {iterable} of vector
	def compress_me(dataset):
		x = dataset

		if learn:
			for i in range(len(operations)): 
				print('Processing ... #{0} : {1}'.format(i,type(operations[i])))
				x = operations[i].fit_transform(x)
		else:
			for i in range(len(operations)): 
				x = operations[i].transform(x)

		return iter(x)
	return compress_me



