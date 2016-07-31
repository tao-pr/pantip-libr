"""
Sparse Matrix to dense matrix conversion
@starcolon projects
"""

from sklearn.base import TransformerMixin

class SparseToDense(TransformerMixin):
  
  def transform(self, X, y=None, **fit_params):
    return X.todense()

  def fit_transform(self, X, y=None, **fit_params):
    self.fit(X, y, **fit_params)
    return self.transform(X)

  def fit(self, X, y=None, **fit_params):
    return self