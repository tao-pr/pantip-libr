"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
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

# Train the vectorizer with the collection (iterable) of text data
def explore(transformer,collection):
	transformer.fit(collection)
	return transformer

# @return {Matrix} Term document matrix
def vectorize(transformer,tokens):
	return transformer.fit_transform(tokens)