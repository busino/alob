'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import os
import pickle
from collections import OrderedDict
import logging

import numpy
from joblib import Parallel, delayed
from skimage.transform._geometric import matrix_transform
from sklearn.pipeline import Pipeline
import sklearn.preprocessing
import sklearn.metrics
import sklearn.svm
import sklearn.decomposition

import alob.ml.features as alob_features
from alob.match import match_images


log = logging.getLogger()


'''
Point Cloud Statistics
----------------------

X:
 min -2.01
 max 8.46710
 median 1.72697287
 mean 1.70563
 std  1.38295

Y:

 min -1.70991
 max  1.69926
 median -0.013069
 mean -0.015
 std  0.6085554
 
'''
    
POINTS_MIN = (-2,-2)
POINTS_MAX = (8, 2)
POINTS_MEAN = (2, 0)
    
def extract_helper(src, dst, search_radius):


    src = src.copy()
    dst = dst.copy()

    src_coords = numpy.array([src['x'], src['y']])
    dst_coords = numpy.array([dst['x'], dst['y']])
    
    src_warts = src_coords[:,4:]
    dst_warts = dst_coords[:,4:]

    #dst_coords = numpy.array([dst['x'], dst['y']])
    #src_coords = numpy.array([src['x'], src['y']])
    #src_initial_points = src[:4]['x'], src[:4]['y']
    #dst_initial_points = dst[:4]['x'], dst[:4]['y']
    
    # Nose and Tail distance
    src_nose = complex(*src[src['type']=='nose'][['x', 'y']][0])
    src_tail = complex(*src[src['type']=='tail'][['x', 'y']][0])
    dst_nose = complex(*dst[dst['type']=='nose'][['x', 'y']][0])
    dst_tail = complex(*dst[dst['type']=='tail'][['x', 'y']][0])
    
    features = OrderedDict(nose_distance=numpy.abs(src_nose-dst_nose), 
                           tail_distance=numpy.abs(src_tail-dst_tail))


    dst_t, (_, _), _, _, result = match_images(src_warts,
                                               dst_warts,
                                               search_radius)
    
    features['match_result_min'] = result/min(src.shape[0], dst.shape[0])
    features['match_result_max'] = result/max(src.shape[0], dst.shape[0])
    features['match_result_mean'] = result/((src.shape[0] + dst.shape[0])/2.)
       
    # transform the point clouds
    #M = affine_matrix_from_points(dst_initial_points, src_initial_points)
    
    #dst_t = matrix_transform(dst_coords.T, M)

    src_pc = src_warts
    dst_pc = dst_t    
    #src_pc_c = src_pc.T.flatten().view(dtype=numpy.complex128)
    #dst_pc_c = dst_pc.T.flatten().view(dtype=numpy.complex128)
    num_points_min = numpy.min([src_pc.shape[1], dst_pc.shape[1]])
    
    pc = numpy.hstack([src_pc, dst_pc])
    
    # Num Points
    features.update(alob_features.NumPoints.p_feature_dict(src_pc, dst_pc))
    
    # Center of Gravity
    features.update(alob_features.CenterOfGravity.p_feature_dict(src_pc, dst_pc))
    
    # Coordinate Statistics
    features.update(alob_features.CoordinateStatistics.p_feature_dict(src_pc, dst_pc))

    # Inertia
    features.update(alob_features.Inertia.p_feature_dict(src_pc, dst_pc))
    
    # Locations
    features.update(alob_features.Locations(center=POINTS_MEAN).p_feature_dict(src_pc, dst_pc))
    
    # Hist 3x3
    N = 4
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_pc[0], src_pc[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_pc[0], dst_pc[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    res = numpy.sum(res)/num_points_min + res.tolist()
    keys = ['hist3x3_sum'] + ['hist3x3_{}'.format(i) for i in range((N-1)**2)]
    #features.update(zip(keys, res))

    # Hist 4x4
    N = 5
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_pc[0], src_pc[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_pc[0], dst_pc[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    res = numpy.sum(res)/num_points_min + res.tolist()
    keys = ['hist4x4_sum'] + ['hist4x4_{}'.format(i) for i in range((N-1)**2)]
    features.update(zip(keys, res))
    
    # Hist 5x5
    N = 6
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_pc[0], src_pc[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_pc[0], dst_pc[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    features['hist5x5_sum'] = numpy.sum(res)/num_points_min
    
    # Matcher
    #matches, _ = MatchPCL(src_pc, dst_pc, search_radius).calc(dst_pc)
    #features['match_result'] = len(matches)/min(src_pc.shape[1], dst_pc.shape[1])
    return features
    

class AlobPairClassifier:
    
    def __init__(self, search_radius, filename=None):
        self.search_radius = search_radius
        if filename == '__default__':
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alob_pair_classifier.pkl'))
        self.filename = filename
        self.pipe = None
        self.labels = [1,0]
        self.pos_label = 1

    def extract_features(self, images, pairs):
        
        log.debug('AlobPairClassifier.extract_features')        
        
        # Only start parallel processing if more than 10000 pairs have to be calculated
        if True:#len(pairs) > 2000:
            pairs_t = Parallel(n_jobs=-2, verbose=0)\
                           (delayed(extract_helper)(images[f], images[s], self.search_radius) 
                            for f,s in pairs)          
        else:
            pairs_t = []
            for f,s in pairs:
                pairs_t.append(extract_helper(images[f], images[s], self.search_radius))
        
        return pairs_t

    def load(self, filename=None):
        log.debug('AlobPairClassifier.load')
        if filename is None and self.filename is None:
            raise RuntimeError('Filename missing.')
        if filename:
            self.filename = filename
        self.pipe = pickle.load(open(self.filename, 'rb'))

    def save(self, filename=None):
        if filename is None and self.filename is None:
            raise RuntimeError('Filename missing.')
        if filename is None:
            filename = self.filename
        if self.pipe is None:
            raise RuntimeError('No Pipe to save.')
        pickle.dump(self.pipe, open(filename, 'wb'))

    def predict(self, images=None, pairs=None, features=None):
        log.debug('AlobPairClassifier.predict')
        if features is None:
            features = self.extract_features(images, pairs)
            features = numpy.array([list(v.values()) for v in features])
        if self.pipe is None:
            self.load()
        res = self.pipe.predict(features)
        return res

    def score(self, labels, predictions):
        log.debug('AlobPairClassifier.score')
        C = sklearn.metrics.confusion_matrix(labels, predictions, labels=self.labels)
        tp = C[0,0]
        fp = C[1,0]
        tn = C[1,1]
        fn = C[0,1]
        pos = fp + tp
        tot = numpy.sum(C)
        n_match = numpy.sum(C[1])
        fn_percentage = fn/n_match*100
        fp_percentage = fp/n_match*100

        percentage = pos/tot*100
        precision = sklearn.metrics.precision_score(labels, predictions, labels=[0,1])
        recall = sklearn.metrics.recall_score(labels, predictions, labels=self.labels, pos_label=self.pos_label)
        acc = sklearn.metrics.accuracy_score(labels, predictions)
        f1_score = sklearn.metrics.f1_score(labels, predictions, labels=self.labels, pos_label=self.pos_label)
        return OrderedDict(C=C, 
                           tp=tp, fp=fp, tn=tn, fn=fn, tot=tot,
                           percentage=percentage, 
                           precision=precision, recall=recall, acc=acc,
                           f1_score=f1_score,
                           fn_percentage=fn_percentage, fp_percentage=fp_percentage
                    )
    
    def fit(self, labels, images=None, pairs=None, features=None):
        log.debug('AlobPairClassifier.fit')
        if features is None:
            features = self.extract_features(images, pairs)
            features = numpy.array([list(v.values()) for v in features])
        pipe = Pipeline([#('scaler', sklearn.preprocessing.MinMaxScaler()),
                         ('scaler', sklearn.preprocessing.StandardScaler()),
                         #('pca', sklearn.decomposition.PCA(n_components=8)),
                         ('pca', sklearn.decomposition.PCA(tol=1e-6, whiten=True, n_components='mle', svd_solver='full')),
                         ('svc', sklearn.svm.SVC(decision_function_shape='ovr', tol=1e-6, kernel='linear', shrinking=True, C=64, class_weight={1: 120}))
                         #('mlp', sklearn.neural_network.MLPClassifier(solver='sgd',#adam, lbfgs,sgd
                         #                                             activation='relu',#'relu',
                         #                                             learning_rate_init=0.001,
                         #                                             batch_size=100,
                         #                                             alpha=1e-6,
                         #                                             tol=1e-6,
                         #                                             verbose=True,
                         #                                             max_iter=12000,
                         #                                             #learning_rate='invscaling',
                         #                                             hidden_layer_sizes=(120, 120, 36),
                         #                                             #random_state=self.random_seed
                         #                                             )),
                         ])
        
        log.debug(' pipe.fit')
        pipe.fit(features, labels)
        self.pipe = pipe
