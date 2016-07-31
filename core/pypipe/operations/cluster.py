"""
Topic category classifier
@starcolon projects
"""

import os
import pickle
from sklearn.cluster import KMeans
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.neighbors.nearest_centroid import NearestCentroid

METHODS = {
	'centroid': NearestCentroid(
		metric='euclidean',#TAOTODO: Any better metric?
		shrink_threshold=None
	)
}

def new(method='centroid',n_features=8):

	# Clustering method
	nc = METHODS[method]

	# Orthogonal feature selector
	selector = SelectKBest(chi2, k=n_features)

	return [selector, nc]

def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the hasher pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path,method,n_features):
	if os.path.isfile(path): return load(path)
	else: return new(method,n_features)

# @return {matrix} if {labels} is supplied
# @return {list} of classification, otherwise
def analyze(clf,labels=None):
	def _do(matrix):
		if labels:  # Learning mode
			X = matrix
			for opr in clf:
				X = clf.fit_transform(X,labels)
			# NOTE: The last operation of the CLF is always a clustering algo
			return clf[-1].predict(matrix)
		else: # Classification mode
			X = matrix
			# Feature transformations
			for opr in clf[:-1]:
				X = opr.transform(X)
			# NOTE: Predict the clusters with the last operation
			y = clf[-1].predict(X)
			return iter(y)
	return _do


