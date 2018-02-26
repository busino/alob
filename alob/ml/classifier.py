import os
import pickle
from collections import OrderedDict
import logging

import numpy
from joblib import Parallel, cpu_count, delayed
from skimage.transform._geometric import matrix_transform
from sklearn.pipeline import Pipeline
import sklearn.preprocessing
import sklearn.metrics
import sklearn.svm
import sklearn.decomposition

import alob.ml.features as alob_features
from alob.affine import affine_matrix_from_points
from alob.match import MatchPCL, match_pc


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


    dst_t, matches, M, result = new_match_images(src,
                                                 dst,
                                                 search_radius)
    
    features['match_result_min'] = result/min(src.shape[0], dst.shape[0])
    features['match_result_max'] = result/max(src.shape[0], dst.shape[0])
    features['match_result_mean'] = result/((src.shape[0] + dst.shape[0])/2.)
       
    # transform the point clouds
    #M = affine_matrix_from_points(dst_initial_points, src_initial_points)
    
    #dst_t = matrix_transform(dst_coords.T, M)

    
    dst['x'][4:] = dst_t[0,4:]
    dst['y'][4:] = dst_t[1,4:]
    
    # prepare point clouds
    src_pc = numpy.array([src[4:]['x'], src[4:]['y']])
    dst_pc = numpy.array([dst[4:]['x'], dst[4:]['y']])
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

    def extract_features(self, images, pairs):
        
        log.debug('AlobPairClassifier.extract_features')        
        
        # Only start parallel processing if more than 10000 pairs have to be calculated
        if len(pairs) > 20000:
            pairs_t = Parallel(n_jobs=cpu_count()-1, verbose=0)\
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
        C = sklearn.metrics.confusion_matrix(labels, predictions)
        tn = C[0,0]
        tp = C[1,1]
        fn = C[1,0]
        fp = C[0,1]
        pos = fp + tp
        tot = numpy.sum(C)
        n_match = numpy.sum(C[1])
        fn_percentage = fn/n_match*100
        fp_percentage = fp/n_match*100

        percentage = pos/tot*100
        precision = sklearn.metrics.precision_score(labels, predictions)
        recall = sklearn.metrics.recall_score(labels, predictions)
        acc = sklearn.metrics.accuracy_score(labels, predictions)
        return dict(C=C, tn=tn, fn=fn, fp=fp, tp=tp, percentage=percentage, 
                    precision=precision, recall=recall, acc=acc,
                    fn_percentage=fn_percentage, fp_percentage=fp_percentage
                    )
    
    def fit(self, labels, images=None, pairs=None, features=None):
        log.debug('AlobPairClassifier.fit')
        if features is None:
            features = self.extract_features(images, pairs)
        pipe = Pipeline([('scaler', sklearn.preprocessing.MinMaxScaler()),
                         ('pca', sklearn.decomposition.PCA(n_components=8)),
                         ('svc', sklearn.svm.SVC(tol=1e-4, kernel='linear', shrinking=True, C=8, class_weight={1: 160}))])
        
        log.debug(' pipe.fit')
        pipe.fit(features, labels)
        self.pipe = pipe
