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
# TAOTOREVIEW: [ShuffleSplit] will be deprecated in 0.18
# and will be moved to [sklearn.model_selection]
from sklearn.cross_validation import ShuffleSplit
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
  print(colored('Cluster model created','yellow'))
  return [selector, nc]

def save(operations,path):
  with open(path,'wb+') as f:
    pickle.dump(operations,f)

def load(path):
  with open(path,'rb') as f:
    print('Cluster model loaded')
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
  def _do(matrix, test_ratio=0.0):
    if labels:  # Learning mode

      # Split train & test folds
      shuffle = ShuffleSplit(len(matrix), test_size=test_ratio)
      trainlist, testlist = [(a,b) for (a,b) in shuffle][-1]
      X_train = [x for x in map(lambda i: matrix[i], trainlist)]
      Y_train = [y for y in map(lambda i: labels[i], trainlist)]
      X_valid = [x for x in map(lambda i: matrix[i], testlist)]
      Y_valid = [y for y in map(lambda i: labels[i], testlist)]

      # Display what the underlying classifier is
      print(colored(clf[-1],'yellow'))

      # Display the dimension of the training elements
      print(colored('Trainset:','cyan'))
      print(colored('X: {0}'.format(np.shape(X_train)),'yellow'))
      print(colored('y: {0}'.format(np.shape(Y_train)),'yellow'))

      # Process trainset
      for opr in clf[:-1]:
        print(colored(opr,'yellow'))
        X_train = opr.fit_transform(X_train,Y_train)
      # NOTE: The last operation of the CLF is always a clustering algo
      clf[-1].fit(X_train,Y_train)

      # Display the dimension of the training elements
      print(colored('Validation set:','cyan'))
      print(colored('X: {0}'.format(np.shape(X_valid)),'yellow'))
      print(colored('y: {0}'.format(np.shape(Y_valid)),'yellow'))

      # Process validation set
      for opr in clf[:-1]:
        print(colored(opr,'yellow'))
        X_valid = opr.transform(X_valid)

      # Return tuple of [actual], [prediction] 
      # on the validation set
      return (Y_valid, clf[-1].predict(X_valid))

    else: # Classification mode
      X = matrix

      # Feature transformations
      for opr in clf[:-1]:
        X = opr.transform(X)

      # NOTE: Predict the clusters with the last operation
      y = clf[-1].predict(X)
      return iter(y)

  return _do


