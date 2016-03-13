"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
import os.path
import pickle
import json
from termcolor import colored
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import NMF
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import TruncatedSVD


# Create a text process pipeline (vectorizer)
def new(n_components=8,stop_words=[]):

	# Prepare vectoriser engines
	idf = TfidfVectorizer(
		ngram_range=(1,3), #Unigram,bigram,& trigram
		stop_words=stop_words
	)

	# Prepare dimentionality reducer
	svd = TruncatedSVD(n_components)

	# Non-negative matrix factorisation (smoother)
	smoother = NMF(init='random')


	# Prepare normaliser
	norm = Normalizer(norm='l2') # Cosine similarity 

	# Prepare task pipeline (in order of operation)
	operations = [
		idf,
		##smoother, TAODEBUG: This causes suspension
		svd,
		norm
	]
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
def safe_load(path,n_components,stop_words):
	if os.path.isfile(path): return load(path)
	else: return new(n_components,stop_words)

def hash(operations,learn=False):
	# @param {iterable} of string
	def hash_me(dataset):
		x = dataset

		if learn:
			for i in range(len(operations)): 
				print('Processing ... #{0} : {1}'.format(i,type(operations[i])))
				x = operations[i].fit_transform(x)
		else:
			for i in range(len(operations)): 
				x = operations[i].transform(x)

		return iter(x)
	return hash_me



