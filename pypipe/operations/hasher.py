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

# Create a text process pipeline (vectorizer)
def new():
	# Prepare vectoriser engines
	hasher = HashingVectorizer(
		n_features=512,
		non_negative=True,
		binary=False)
	idf = TfidfVectorizer()
	return make_pipeline(hasher,idf)

def vectorize(vectorizer,tokens):
	return vectorizer.fit_transform(tokens)