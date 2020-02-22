'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import logging
import os
import pickle
from collections import OrderedDict

import numpy
from joblib import Parallel, delayed
from sklearn.pipeline import Pipeline
import sklearn.preprocessing
import sklearn.metrics

from alob.ml.estimator import RoughEstimator
import alob.ml.features as alob_features
from alob.match import match_pc


log = logging.getLogger(__name__)

#
# Information extracted with preprocessing script
#
POINTS_MIN = (-1,-1.65)
POINTS_MAX = (9, 1.65)
POINTS_MEAN = (2.4, 0)


def extract_helper(src, dst, search_radius):

    src = src.copy()
    dst = dst.copy()

    #dst_coords = numpy.array([dst['x'], dst['y']])
    #src_coords = numpy.array([src['x'], src['y']])
    #src_initial_points = src[:4]['x'], src[:4]['y']
    #dst_initial_points = dst[:4]['x'], dst[:4]['y']
    
    # Nose and Tail distance
    src_nose = complex(*src[src['type']=='nose'][['x', 'y']][0])
    src_tail = complex(*src[src['type']=='tail'][['x', 'y']][0])
    dst_nose = complex(*dst[dst['type']=='nose'][['x', 'y']][0])
    dst_tail = complex(*dst[dst['type']=='tail'][['x', 'y']][0])
    
    #
    # Nose/Tail Distance
    #
    # TODO remove tail distance
    features = OrderedDict(nose_distance=numpy.abs(src_nose-dst_nose), 
                           tail_distance=numpy.abs(src_tail-dst_tail))

    src_coords = numpy.array([src['x'], src['y']])
    dst_coords = numpy.array([dst['x'], dst['y']])

    src_warts = src_coords[:,4:]
    dst_warts = dst_coords[:,4:]
    
    #
    # Coarse matches
    #
    _, _, num_matches = match_pc(src_warts,
                                 dst_warts,
                                 search_radius)
    
    features['matches_diff_min'] = float(min(src_warts.shape[1], dst_warts.shape[1]) - num_matches)
    features['match_result_min'] = 1. - num_matches/min(src_warts.shape[1], dst_warts.shape[1])
    features['match_result_max'] = 1. - num_matches/max(src.shape[0], dst.shape[0])
    features['match_result_mean'] = 1. - num_matches/((src.shape[0] + dst.shape[0])/2.)
       
    num_points_min = numpy.min([src_warts.shape[1], dst_warts.shape[1]])
    
    # Num Points
    features.update(alob_features.NumPoints.p_feature_dict(src_warts, dst_warts))
    
    # Center of Gravity
    features.update(alob_features.CenterOfGravity.p_feature_dict(src_warts, dst_warts))
    
    # Coordinate Statistics
    features.update(alob_features.CoordinateStatistics.p_feature_dict(src_warts, dst_warts))

    # Inertia
    features.update(alob_features.Inertia.p_feature_dict(src_warts, dst_warts))
    
    # Locations
    features.update(alob_features.Locations(center=POINTS_MEAN).p_feature_dict(src_warts, dst_warts))
    
    # Hist 3x3
    N = 4
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_warts[0], src_warts[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_warts[0], dst_warts[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    res = numpy.sum(res)/num_points_min + res.tolist()
    keys = ['hist3x3_sum'] + ['hist3x3_{}'.format(i) for i in range((N-1)**2)]
    #features.update(zip(keys, res))

    # Hist 4x4
    N = 5
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_warts[0], src_warts[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_warts[0], dst_warts[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    res = numpy.sum(res)/num_points_min + res.tolist()
    keys = ['hist4x4_sum'] + ['hist4x4_{}'.format(i) for i in range((N-1)**2)]
    features.update(zip(keys, res))
    
    # Hist 5x5
    N = 6
    xedges = numpy.linspace(POINTS_MIN[0], POINTS_MAX[0], N)
    yedges = numpy.linspace(POINTS_MIN[1], POINTS_MAX[1], N)
    
    src_hist, _, _ = numpy.histogram2d(src_warts[0], src_warts[1], bins=(xedges, yedges))
    dst_hist, _, _ = numpy.histogram2d(dst_warts[0], dst_warts[1], bins=(xedges, yedges))
    res = numpy.abs(src_hist.flatten()-dst_hist.flatten())
    features['hist5x5_sum'] = numpy.sum(res)/num_points_min
    
    #
    # Summarize all features
    #
    features['sum'] = sum(features.values())
    
    return features

def f_helper(image_features, pc):
    return [f(pc) for f in image_features]

def p_helper(rpm, f, s, f_f, s_f):
    return [rpm(f,s)] + numpy.abs(f_f-s_f).tolist()

def p2_helper(image_features, f, s):
    f_v = []
    for i,feature in enumerate(image_features):
        f_v.extend(feature.pair_v(f[i],s[i]))
    return f_v
    
    
class Preselect:
    
    def __init__(self, search_radius, filename=None):
        self.search_radius = search_radius
        if filename == '__default__':
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'alob_pair_preselect.pkl'))
        self.filename = filename
        self.pipe = None

    def extract_features(self, images, pairs):
        
        log.debug('Preselect.extract_features')        
        
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
        log.debug('Preselect.load')
        if filename is None and self.filename is None:
            raise RuntimeError('Filename missing.')
        if filename:
            self.filename = filename
        self.pipe = pickle.load(open(self.filename, 'rb'))

    def save(self, filename=None):
        log.debug('Preselect.save')
        if filename is None and self.filename is None:
            raise RuntimeError('Filename missing.')
        if filename is None:
            filename = self.filename
        if self.pipe is None:
            raise RuntimeError('No Pipe to save.')
        pickle.dump(self.pipe, open(filename, 'wb'))

    def predict(self, images=None, pairs=None, features=None):
        log.debug('Preselect.predict')
        if features is None:
            features = self.extract_features(images, pairs)
            features = numpy.array([list(v.values()) for v in features])
        self.load()
        res = self.pipe.predict(features)
        return res

    def score(self, labels, predictions):
        log.debug('Preselect.score')
        if not isinstance(labels, list):
            labels = list(labels)
        if not isinstance(predictions, list):
            predictions = list(predictions)
            
        C = sklearn.metrics.confusion_matrix(labels, predictions)
        tn = C[0,0]
        tp = C[1,1]
        fn = C[1,0]
        fp = C[0,1]
        pos = fp + tp
        tot = numpy.sum(C)
        percentage = pos/tot*100
        return dict(C=C, tn=tn, fn=fn, fp=fp, tp=tp, selected_percentage=percentage)
    
    def fit(self, labels, images=None, pairs=None, features=None):
        log.debug('Preselect.fit')
        if features is None:
            features = self.extract_features(images, pairs)
            features = numpy.array([list(v.values()) for v in features])
        pipe = Pipeline([('scaler', sklearn.preprocessing.StandardScaler()),
                         ('rest', RoughEstimator())])
        
        pipe.fit(features, labels)
        self.pipe = pipe
