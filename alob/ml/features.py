'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import logging
import numpy

from alob.match import match_images, MatchPCL


log = logging.getLogger(__name__)


class FeatureBase:
    '''
    Base Class for Features
    
    Attributes
    ----------
        
        name: str
            Name of the Feature
        keys: list(str)
            Names of the including features
    '''
    
    name = 'FeatureBase'
    keys = []
    
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    @staticmethod
    def feature(pc):
        raise NotImplementedError('feature function have to be implemented in inherit class.')
    
    @classmethod
    def p_feature(cls, src, dst):
        return numpy.abs(cls.feature(src) - cls.feature(dst))
    
    @classmethod
    def p_feature_dict(cls, src, dst):
        return dict(zip(cls.keys, cls.p_feature(src, dst)))


class NumPoints(FeatureBase):
    '''
    Number of Points
    '''
    
    name = 'NumPoints'
    keys = ['num_points']
    
    @staticmethod
    def feature(pc):
        return numpy.array([pc.shape[1]], dtype=numpy.float64)


class CoordinateStatistics(FeatureBase):
    
    name = 'CoordinateStatistics'
    keys = ['x_min', 'y_min',
            'x_max', 'y_max',
            'x_mean', 'y_mean',
            'x_stddev', 'y_stddev',
            'x_median', 'y_median',
            'x_width', 'y_width']

    @staticmethod
    def feature(pc):
        return numpy.array([pc.min(axis=1), pc.max(axis=1), pc.mean(axis=1), pc.std(axis=1), numpy.median(pc, axis=1), pc.ptp(axis=1)]).flatten()


class Locations(FeatureBase):
    '''
    Point Locations
    left, right, lower, upper, lower-left, lower-right, upper-left, upper-right
    
    Parameters
    ----------
        center : tuple
            center-point to divide point cloud
    '''    
    name = 'Locations'
    keys = ['n_left', 'n_right', 'n_lower', 'n_upper', 'n_ll', 'n_ul', 'n_lr', 'n_ur']

    def __init__(self, center):
        self.center = center

    @staticmethod
    def feature(pc, center):
        
        n_left = numpy.sum(pc[0] <= center[0])
        n_right = numpy.sum(pc[0] > center[0])
    
        n_lower = numpy.sum(pc[1] <= center[1])
        n_upper = numpy.sum(pc[1] > center[1])
        
        n_ll = numpy.sum( (pc[0] <= center[0]) & (pc[1] <= center[1]))
        n_ul = numpy.sum( (pc[0] <= center[0]) & (pc[1] > center[1]))
        
        n_lr = numpy.sum( (pc[0] > center[0]) & (pc[1] <= center[1]))
        n_ur = numpy.sum( (pc[0] > center[0]) & (pc[1] > center[1]))
                
        return numpy.array([n_left, n_right, n_lower, n_upper, n_ll, n_ul, n_lr, n_ur], dtype=numpy.float64)    

    def p_feature(self, src, dst):
        center = self.center
        return numpy.abs(self.feature(src, center) - self.feature(dst, center))

    def p_feature_dict(self, src, dst):
        return dict(zip(self.keys, self.p_feature(src, dst)))

class CenterOfGravity(FeatureBase):
    
    name = 'CenterOfGravity'
    keys = ['cog']

    @staticmethod
    def feature(pc):
        pc_c = pc.T.flatten().view(dtype=numpy.complex128).reshape(-1,1)
        return numpy.array([numpy.sum(pc_c)/pc_c.shape[0]])


class Inertia(FeatureBase):
    
    name = 'Inertia'
    keys = ['inertia_x', 'inertia_y']

    @staticmethod
    def feature(pc):
        return numpy.mean(numpy.power(pc, 2), axis=-1)


class Position2dHistogramm3x3(FeatureBase):
    '''
    3x3 2d Histogramm of Points
    '''

    name = 'Position2dHistogramm3x3'
    keys = ['hist3x3_{}'.format(i) for i in range(3**2)]
    
    def __impl(self, pc):

        X_MIN, X_MAX = self.x_range
        Y_MIN, Y_MAX = self.y_range
        pcc = pc[0]+1j*pc[1]
        
        N = 4
        xedges = numpy.linspace(X_MIN, X_MAX, N)
        yedges = numpy.linspace(Y_MIN, Y_MAX, N)
        
        hist, _, _ = numpy.histogram2d(pcc.real, pcc.imag, bins=(xedges, yedges))
        #hist /= numpy.max(hist)
        
        return hist.flatten()

    def __pair_impl(self, f, s):
        '''
        Feature value for a pair of features
        '''
        f = numpy.abs(numpy.array(f) - numpy.array(s)).tolist()
        return [numpy.sum(f)] + f


class Position2dHistogramm4x4(FeatureBase):
    '''
    4x4 2d Histogramm of Points
    '''

    name = 'Position2dHistogramm4x4'
    keys = ['hist4x4_{}'.format(i) for i in range(4**2)]
    
    def __impl(self, pc):

        X_MIN, X_MAX = self.x_range
        Y_MIN, Y_MAX = self.y_range
        pcc = pc[0]+1j*pc[1]
        
        N = 5
        xedges = numpy.linspace(X_MIN, X_MAX, N)
        yedges = numpy.linspace(Y_MIN, Y_MAX, N)
        
        hist, _, _ = numpy.histogram2d(pcc.real, pcc.imag, bins=(xedges, yedges))
        #hist /= numpy.max(hist)
        
        return hist.flatten()

    def __pair_impl(self, f, s):
        '''
        Feature value for a pair of features
        '''
        f = numpy.abs(numpy.array(f) - numpy.array(s)).tolist()
        return [numpy.sum(f)] + f


class PointDistancesHist(FeatureBase):
    
    name = 'PointDistancesHist'
    keys = ['pd_hist{}'.format(i) for i in range(20)]
    
    def __impl(self, pc):
        pc = pc[0]+1j*pc[1]
        pcm = numpy.matrix(pc)
        distances = numpy.abs((pcm-pcm.T))[numpy.triu_indices(pcm.shape[1],k=1)]
        h, _ = numpy.histogram(distances, bins=10, range=(10, 80))
        return h


class RoughPointMatching(FeatureBase):

    name = 'PointMatching'
    keys = ['rough_matching_result']

    def __impl(self, pc1, pc2):
        
        matcher = MatchPCL(pc1, pc2, self.search_radius)
        matches, _ = matcher.calc(pc2)
        res = len(matches)/min(pc1.shape[1], pc2.shape[1])
        return [res]
    

class PointMatching(FeatureBase):
    
    name = 'PointMatching'
    keys = ['matching_result']
    
    def __impl(self, pc1, pc2):
        _,_,_,_, res = match_images(pc1, pc2, self.search_radius)
        res = res/min(pc1.shape[1], pc2.shape[1])
        return [res]
