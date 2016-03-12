"""
Unsupervised topic classification
@starcolon projects
"""

import os
import pickle
from sklearn.cluster import KMeans

def new(n_labels=10):
	kmeans = KMeans(
		n_clusters = n_labels,
		n_jobs = 2
	)

	return kmeans

def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the hasher pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path,n_labels):
	if os.path.isfile(path): return load(path)
	else: return new(n_labels)

def classify(clf,learn=True):
	def _do(matrix):
		if learn: return iter(clf.fit_predict(matrix))
		else: return iter(clf.predict(matrix))
	return _do