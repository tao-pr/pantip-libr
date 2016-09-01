"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
import os.path
import pickle
import json
import math
import sys
from .sparsetodense import SparseToDense
from termcolor import colored
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import TruncatedSVD
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import IncrementalPCA
from sklearn.decomposition import SparsePCA

_1GB = 1073741824


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

	s = pickle.dumps(operations, pickle.HIGHEST_PROTOCOL)
	z = sys.getsizeof(s)
	print('texthasher model occupies total size of {0:.2f} GB'.format(z/_1GB))

	# In case of huge model, split it into smaller chunks 
	# and save seperately
	if z>_1GB:
		i = 0
		for c in split_to_chunks(s,_1GB):
			i += 1
			save_chunk(path, i, c)
	else:
		# Small model, just save it with typical method
		with open(path + '.0', 'wb+') as f:
			pickle.dump(operations, f)

def save_chunk(path,i,chunk):
	with open(path + '.' + str(i), 'wb+') as f:
		print(colored('Saving chunk #{0} '.format(i), 'yellow'))
		pickle.dump(chunk, f)

# Split a bulky string into multiple parts by given size
def split_to_chunks(bulky_str,chunk_size):
	
	pos,i,tot = 0, 0, len(bulky_str)

	while pos<tot:
		if pos+chunk_size >= tot:
			chunk = bulky_str[pos:]
		else:
			chunk = bulky_str[pos:pos+chunk_size]
		
		yield chunk
		i   += 1
		pos += chunk_size


def load(path):
	i = 0
	s = ''
	# Load all chunks, assembly them into one single object
	while os.path.isfile(path + '.' + str(i)):
		print(colored('Loading chunk #{0}'.format(i), 'yellow'))
		with open(path + '.' + str(i),'rb') as f:
			s += pickle.load(f)
	
	return pickle.loads(s)


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



