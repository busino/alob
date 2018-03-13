'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import numpy
from sklearn.base import BaseEstimator, ClassifierMixin


class RoughEstimator(BaseEstimator, ClassifierMixin):
    
    def __init__(self):
        #self._min = []
        self._max = []
    
    def fit(self, X, y):
        #
        # TODO select 90 to 95 percent
        # define min cut and not min max cut
        #
        features = numpy.array(X)
        labels = numpy.array(y).astype(bool)
        matches = features[labels]
        #min_ = numpy.min(matches, axis=0)
        max_ = numpy.max(matches, axis=0)
        #self._min = min_
        self._max = max_
        return self

    def predict(self, X):
        X = numpy.array(X)
        results = numpy.all(X <= self._max, axis=1)
        return results.astype(numpy.int)