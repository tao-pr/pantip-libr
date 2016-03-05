"""
Topic category classifier
@starcolon projects
"""

from sklearn.cluster import KMeans

def new(num_class):
	kmean = KMeans(
		n_clusters=num_class,
		max_iter=64,
		n_init=1
		)

	return [kmean]

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

def analyze(operations,learn=False):
	def _do(matrix):
		m = matrix
		for i in range(len(operations)):
			if learn: m = operations[i].fit_transform(m) #TAOTODO: Kmean doesn't transform
			else: m = operations[i].transform(m)
			return m
	return _do

