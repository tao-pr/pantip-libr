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
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import SparsePCA


# Create a text process pipeline (vectorizer)
def new(n_components=None,stop_words=[],decomposition='SVD'):

	# Prepare vectoriser engines
	idf = TfidfVectorizer(
		ngram_range=(1,3), #Unigram,bigram,& trigram
		stop_words=stop_words
	)

	# Prepare normaliser
	norm = Normalizer(norm='l2') # Cosine similarity 

	# Prepare dimentionality reducer
	if n_components:
		if decomposition=='LDA':
			reducer = LatentDirichletAllocation( # TFIDF --> Topic term
				n_topics=n_components,
				max_iter=15	
			)
		elif decomposition=='SVD':
			reducer = TruncatedSVD(n_components,n_iter=15) # Damn slow
		elif decomposition=='PCA':
			reducer = SparsePCA(n_components,alpha=1.,max_iter=15)
		else:
			return [idf,norm]

		return [idf,reducer,norm]
	else:
		return [idf,norm]


def save(operations,path):
	print('Saving texthasher model...')
	with open(path,'wb+') as f:
		pickle.dump(operations,f,protocal=4)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f,protocal=4)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path,n_components,stop_words,decomposition):
	if os.path.isfile(path) and os.stat(path).st_size>0: return load(path)
	else: return new(n_components,stop_words,decomposition)

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



