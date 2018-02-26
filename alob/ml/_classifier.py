import logging
import pickle

from joblib import Parallel, delayed
import numpy

from . import *
from sklearn.pipeline import Pipeline
import sklearn.preprocessing
import sklearn.svm


log = logging.getLogger('alob')

available_classifiers = []


class ClassifierAlgoBase:

    name = 'classifier_algo_base'
    
    def __repr__(self):
        return '{}'.format(self.name)

# TODO
# multiprocessing working!!!!
def p_fv(args, **kwargs):
    return ClassifierAlgo.pair_feature_vec(*args, *kwargs)
    
    
class ClassifierAlgo(ClassifierAlgoBase):
    '''
    
    Pair Classifier Class to be used to classify pairs of images
    This class is persistent and can be saved to files and byte objects using pickle
    
    Attributes
    ----------
    
        feature_names: list(Features.name)
            list of features to be used
        feature_args: list(dict)
            list of feature class arguments
    
    '''
    
    name = 'AlobPointCloudPairClassifier'
    
    def __init__(self, features):

        self.features = []
        self.classifier_pipeline = None
        self.trained = False
        
        # initialize the features
        single_features, pair_features = [], []
        for feature in features:
            if feature.type == 'single':
                single_features.append(feature)
            else:
                pair_features.append(feature)
    
        self.features = single_features + pair_features
    
        # initialize the classifier
        pipe = Pipeline([('scaler', sklearn.preprocessing.StandardScaler()),
                         ('svc', sklearn.svm.SVC(kernel='linear', C=0.01, class_weight={1: 8}))])

        self.classifier_pipeline = pipe

    def __repr__(self):
        return '{}(name={}, trained={})'.format(self.__class__.__name__, self.name, self.trained)

    @property
    def feature_names(self):
        l = []
        [l.extend(f.keys) for f in self.features]
        return l

    @property
    def num_feature_values(self):
        return len(self.feature_names)

    def pair_feature_vec(self, pc):

        pc_1, pc_2 = pc
        f_1 = self.feature_vec(pc_1)
        f_2 = self.feature_vec(pc_2)

        # make it a pair feature vector
        f = numpy.abs(numpy.array(f_1) - numpy.array(f_2))
        
        # run over the pair features and add them
        pair_f = [feature(pc_1, pc_2) for feature in self.features if feature.type == 'pair']

        return f.tolist() + pair_f

    def feature_vec(self, pc):
        f_values = []
        [f_values.extend(feature(pc)) for feature in self.features if feature.type == 'single']
        return f_values

    def feature_values(self, point_cloud_pairs):

        # TODO
        # Multiprocessing enabled
        if False:
            p = Parallel(n_jobs=5, backend="multiprocessing")
            f_values = p(delayed(p_fv)(i) for i in zip([self]*len(point_cloud_pairs), point_cloud_pairs))
            f_values = numpy.array(object=f_values,
                                   dtype=numpy.float64)
        else:
            f_values = numpy.ndarray(shape=(len(point_cloud_pairs), self.num_feature_values), 
                                     dtype=numpy.float64)
            for i, pc in enumerate(point_cloud_pairs):
                f_values[i] = self.pair_feature_vec(pc)
        
        return f_values

    def train(self, point_cloud_pairs, labels):
        f_values = self.feature_values(point_cloud_pairs).tolist()
        self.classifier_pipeline.fit(f_values, labels)
        self.trained = True
    
    def predict(self, point_cloud_pairs):
        if not self.trained:
            raise RuntimeError('Classifier not ready! Have to be trained first.')
        
        f_values = self.feature_values(point_cloud_pairs)
        result = self.classifier_pipeline.predict(f_values.tolist())
        return result
    
    def save(self, filename=None):
        d = {}
        d['classifier_pipeline'] = self.classifier_pipeline
        d['trained'] = self.trained
        d['features'] = str(self.features)
        if filename:
            with open(filename, 'wb') as f:
                data = pickle.dump(d, f)
        else:
            data = pickle.dumps(d)

        return data
    
    @classmethod
    def load(cls, data=None, filename=None):

        # load from file
        if filename is not None:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        else:
            data = pickle.loads(data)

        features = eval(data['features'])
        inst = cls(features=features)
        for v in ['classifier_pipeline', 'trained']:
            setattr(inst, v, data.get(v))
        
        return inst

