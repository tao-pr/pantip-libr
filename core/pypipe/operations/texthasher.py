"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
import os.path
import pickle
import json
from .sparsetodense import SparseToDense
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
from sklearn.decomposition import IncrementalPCA
from sklearn.decomposition import SparsePCA

# Create a text process pipeline (vectorizer)
def new(stop_words=[],decomposition='SVD',n_components=5):

	# Prepare vectoriser engines
	idf = TfidfVectorizer(
		ngram_range=(1,3), #Unigram,bigram,& trigram
		stop_words=stop_words
	)

	# Prepare normaliser
	# TAOTODO: Needs to be non-negative normaliser
	norm = Normalizer(norm='max')

	# Prepare dimensionality reduction
	if decomposition and n_components:
		if decomposition=='LDA': # Results in Non-negative matrix
			reducer = LatentDirichletAllocation( # TFIDF --> Topic term
				n_topics=n_components,
				max_doc_update_iter=20,
				max_iter=8	
			)
			return [idf,norm,reducer]

		elif decomposition=='SVD':
			reducer = TruncatedSVD( # Best for small dataset, 
				n_components,         # nightmare for large dataset
				n_iter=8) # Damn slow

			return [idf,norm,reducer]

		elif decomposition=='PCA':
			# When using IPCA, remember to always keep:
			# n_samples > n_components > batch_size
			# reducer = IncrementalPCA(n_components)

			# Sparse -> Dense greedily consumes large amount of mem
			# to_dense = SparseToDense()

			# return [idf,norm,to_dense,reducer]

			reducer = SparsePCA(n_components)
			return [idf,norm,reducer]

		return [idf,norm]
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
def safe_load(path,stop_words,decomposition,n_components):
	if os.path.isfile(path) and os.stat(path).st_size>0: return load(path)
	else: return new(stop_words,decomposition,n_components)

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



