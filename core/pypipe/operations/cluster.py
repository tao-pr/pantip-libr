"""
Topic category classifier
@starcolon projects
"""

import pickle
from sklearn.cluster import KMeans
from sklearn.neighbors.nearest_centroid import NearestCentroid

def new():
	# kmean = KMeans(
	# 	n_clusters=num_class,
	# 	max_iter=64,
	# 	n_init=1
	# 	)
	nc = NearestCentroid(
		metric='euclidean',
		shrink_threshold=None
	)

	return nc

def save(operations,path):
	with open(path,'wb+') as f:
		pickle.dump(operations,f)

def load(path):
	with open(path,'rb') as f:
		return pickle.load(f)

# Load the hasher pipeline object
# from the physical file,
# or initialise a new object if the file doesn't exist
def safe_load(path):
	if os.path.isfile(path): return load(path)
	else: return new()

# @return {matrix} if {labels} is supplied
# @return {list} of classification, otherwise
def analyze(clf,labels=None):
	def _do(matrix):
		if labels:  # Learning mode
			clf.fit(matrix,labels)
			return matrix
		else: # Classification mode
			y = clf.predict(matrix)
			return y
	return _do


