"""
Text hashing vectoriser module
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
from sklearn.linear_model import RidgeClassifier
from sklearn.neighbors import NearestCentroid
from sklearn.preprocessing import Normalizer
from sklearn.pipeline import make_pipeline
from sklearn.decomposition import PCA


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

	# Prepare task pipeline
	vectorizer = [idf,hasher]
	preprocess = [pca]
	return (vectorizer,preprocess)

def save(transformer,path):
	with open(path,'wb+') as f:
		pickle.dump(transformer,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the transformer pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path):
	if os.path.isfile(path): return load(path)
	else: return new()

def hash(transformer,learn=False):
	(vectorizer,preprocess) = transformer
	def hash_me(text):
		x = text
		if learn:
			for i in len(vectorizer):
				x = vectorizer[i].fit_transform(x)
			x = preprocess.fit_transform(x)
		else:
			for i in len(vectorizer):
				x = vectorizer[i].transform(x)
			x = preprocess.transform(x)
		return x
	return hash_me



