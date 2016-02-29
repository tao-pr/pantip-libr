"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
import os.path
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.decomposition import PCA
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import make_pipeline

# Create a text process pipeline (vectorizer)
def new():
	# Prepare vectoriser engines
	hasher = HashingVectorizer(
		n_features=512,
		non_negative=True,
		binary=False)
	idf = TfidfVectorizer()

	# Prepare dimentionality reducer
	pca = PCA(n_components=64)

	# Prepare two principal processes
	transformer = [hasher,idf,pca] # Order matters
	return transformer

def save(transformer,path):
	with open(path,'wb+') as f:
		pickle.dump(transformer)

def load(path):
	with open(path,'rb') as f: #TAOTODO: Should extract pipeline beforehand
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path):
	if os.path.isfile(path): return load(path)
	else: return new()

# Train the vectorizer with the collection (iterable) of text data
# @return {Tuple(a,b)} where a:transformer, b: transformation results
def train(transformer):
	seq_opr = make_pipeline(transformer)
	def _train_on(collection):
		# Fit the model and also returns the transformation results
		collection_ = seq_opr.fit_transform(collection)
		# TAOTODO: After pipeline processing, does each of the 
		# collection gets updated??
		return (transformer,collection_)
	return _train_on

# @return {Matrix} Term document matrix with dimension reduction
def vectorize(transformer):
	seq_opr = make_pipeline(transformer)
	def _vectorize_on(collection):
		return seq_opr.transform(collection)
	return _vectorize_on


