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
	transformer = make_pipeline(hasher,idf,pca)
	return transformer

def save(transformer,path):
	with open(path,'wb+') as f:
		pickle.dump(transformer)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path):
	if os.path.isfile(path): return load(path)
	else: return new()

# Train the vectorizer with the collection (iterable) of text data
def explore(collection):
	def _explore_with(transformer):
		transformer.fit(collection)
		return transformer
	return _explore_with

# @return {Matrix} Term document matrix
def vectorize(tokens):
	def _vectorize_with(transformer):
		return transformer.fit_transform(tokens)
	return _vectorize_with