"""
Topic category classifier
@starcolon projects
"""

import os
import pickle
import numpy as np
from termcolor import colored
from sklearn.svm import SVC
from sklearn.cluster import KMeans
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors.nearest_centroid import NearestCentroid
from sklearn.qda import QDA
from sklearn.linear_model import SGDClassifier

METHODS = {
	'centroid': NearestCentroid(
		metric='euclidean',#TAOTOREVIEW: Any better metric?
		shrink_threshold=None
	),
	'knn': KNeighborsClassifier(
    n_neighbors=8,
    weights='distance',
    algorithm='kd_tree'
  ),
  'qda': QDA(),
  'sgd': SGDClassifier(
  	loss='squared_loss',
  	penalty='l2', # Equivalent to SVM (Norm-2)
  	n_iter=10
  ),
  'svm': SVC(
  	kernel='rbf', gamma=0.1,
  	C=1.0
  )
}

def new(method='centroid',n_features=8):

	# Clustering method
	nc = METHODS[method]

	# Orthogonal feature selector
	if n_features is None: n_features = 'all'
	selector = SelectKBest(f_classif, k=n_features)

	# NOTE: The only last operation of the list
	# must be a classifier or clustering model
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

			# Display what the underlying classifier is
			print(colored(clf[-1],'yellow'))

			# Display the dimension of the training elements
			print(colored('X: {0}'.format(np.shape(X)),'yellow'))
			print(colored('y: {0}'.format(np.shape(labels)),'yellow'))

			for opr in clf[:-1]:
				print(colored(opr,'yellow'))
				X = opr.fit_transform(X,labels)

			# NOTE: The last operation of the CLF is always a clustering algo
			clf[-1].fit(X,labels)
			return clf[-1].predict(X)

		else: # Classification mode
			X = matrix
			# Feature transformations
			for opr in clf[:-1]:
				X = opr.transform(X)

			# NOTE: Predict the clusters with the last operation
			y = clf[-1].predict(X)
			return iter(y)

	return _do


