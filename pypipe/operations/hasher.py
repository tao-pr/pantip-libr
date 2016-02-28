"""
Text hashing vectoriser module
@starcolon projects
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import make_pipeline

def new():
	# Prepare vectoriser engines
	hasher = HashingVectorizer(
		n_features=512,
		non_negative=True,
		binary=False)
	return hasher

def vectorize(hasher,tokens):
	return hasher.fit_transform(tokens)