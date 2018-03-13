'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
from cmath import rect
import logging
from itertools import product, combinations

import numpy
from skimage.transform._geometric import matrix_transform

from .affine import affine_matrix_from_points


log = logging.getLogger(__name__)


class MatchPCL(object):

    def __init__(self, first, second, search_radius):
        m1 = first[0] + 1j*first[1]
        self.n1 = m1.size
        n2 = second.shape[1]
        self.m1 = numpy.hstack([(m1,)*n2])
        self.search_radius = search_radius
        
    def calc(self, second):
        m2 = second[0] + 1j*second[1]
        m2 = numpy.hstack([(m2,)*self.n1])
        distances = numpy.abs(self.m1.T - m2)
        
        #first_matching_points = set(numpy.argwhere(distances < self.search_radius)[:,0])
        #second_matching_points = set(numpy.argwhere(distances < self.search_radius)[:,1])

        matches = numpy.zeros_like(distances, dtype=numpy.int64)
        matches[distances < self.search_radius] = 1
        sorted_matches = numpy.argsort(numpy.sum(matches,axis=1))
        first_match_list = []
        second_match_list = []
        for m in sorted_matches:
            for k in numpy.argwhere(matches[m]>0):
                matches[:,k] = 0
                first_match_list.append(m)
                second_match_list.append(k[0])
                break
        #print(len(first_match_list), len(first_matching_points), len(second_matching_points))
        #if sorted(first_match_list) != sorted(second_matching_points):
        #    print('  first: ', sorted(first_match_list), sorted(second_matching_points))
        #if sorted(second_match_list) != sorted(first_matching_points):
        #    print('  second: ', sorted(second_match_list), sorted(first_matching_points))
        return first_match_list, second_match_list

def match_point_clouds(first, second, search_radius=6):
    
    m1 = first[0] + 1j*first[1]
    m2 = second[0] + 1j*second[1]
    
    n1 = m1.size
    n2 = m2.size
    
    m1 = numpy.hstack([(m1,)*n2])
    m2 = numpy.hstack([(m2,)*n1])

    distances = numpy.abs(m1.T - m2)
    
    # extract minimal distances
    '''
    pairs = []
    for i in range(min(n1,n2)):
        amin = numpy.unravel_index(numpy.argmin(distances), distances.shape)
        v = distances[amin]
        distances[amin[0]] = 99999999
        distances[:,amin[1]] =99999999           
        pairs.append((amin[0], amin[1], v))    
    '''
    
    # find distances in search_radius
    second_matching_points = set(numpy.argwhere(distances < search_radius)[:,1])
    
    return second_matching_points

def trans_params(M):
    '''Extract transformation params from 2-D transformation matrix
    Input:
      - `M`: Transformation Matrix 3x3
    Return:
      - `(t_x, t_y)`: Translation in x and y
      - `rot`: Rotation in angle
      - `shear`: Shear in angle
      - `(s_x, s_y)`: Scaling factor in x and y 
    '''
    rot = numpy.arctan2(M[1, 0], M[0, 0])
    beta = numpy.arctan2(- M[0, 1], M[1, 1])
    shear = beta - rot
    return M[0:2, 2], rot*180./numpy.pi, shear*180./numpy.pi, (numpy.sqrt(M[0, 0] ** 2 + M[1, 0] ** 2), numpy.sqrt(M[0, 1] ** 2 + M[1, 1] ** 2))

def area(x, y):
    return 0.5*numpy.abs(numpy.dot(x,numpy.roll(y,1))-numpy.dot(y,numpy.roll(x,1)))


def match_pc(src, dst, search_radius):

    src_matches, dst_matches = MatchPCL(src, dst, search_radius).calc(dst)
    num_matches = len(dst_matches)
    return src_matches, dst_matches, num_matches


def match_images(src, dst, search_radius):
    '''
    match two point clouds
    Input:
      - `src`: source point cloud
      - `dst`: point cloud to match to source
      - `search_radius`: radius to match points
    Return:
      - `corrected`: corrected point cloud
      - `matches`: (src, dst) matching points
      - `transform`: transformation matrix
      - `ref_ids`: ref_ids of points used to calculate matching
      - `res`: matching points
    '''

    #t = numpy.vstack([dst, numpy.ones((1, dst.shape[1]))])

    matcher = MatchPCL(src, dst, search_radius)
    src_size = src.shape[1]
    dst_size = dst.shape[1]

    # initial match with no transformation
    dst_corrected = dst
    matches, second_matches = matcher.calc(dst)
    dst_matching_points = matches
    src_matching_points = second_matches
    result = len(matches)
    ref_ids = numpy.empty(shape=(0,0))
    transform = numpy.eye(3,3)
    
    MAX_TRANSLATION = 8.*search_radius
    
    point_combinations = initial_points(src, dst)   

    for c in point_combinations:
        
        # check that only valid combinations are calculated
        if numpy.any(numpy.diff(numpy.sort(c, axis=0), axis=0) == 0):
            #print('Ignoring combination: {}'.format(c))
            continue

        # check the geometry of the combination
        # 
        #
        # check the area of the polygon
        #area_relation = numpy.abs(area(*dst.T[c[:,1]].T)/area(*src.T[c[:,0]].T))
        #if area_relation > 25:
        #    #print('Area bad: {}'.format(area_relation))
        #    continue
        M = affine_matrix_from_points(dst.T[c[:,1]].T, src.T[c[:,0]].T)

        (t_x, t_y), rot, shear, (scale_x, scale_y) = trans_params(M)
        if abs(rot) > 9.:
            #print('rot: %s'%rot)
            continue
        if abs(t_x) > MAX_TRANSLATION:
            #print('t_x: %s'%t_x)
            continue
        if abs(t_y) > MAX_TRANSLATION:
            #print('t_y: %s'%t_x)
            continue
        if abs(1-scale_x) > 0.16:
            #print('s_x: %s'%abs(1-scale_x))
            continue
        if abs(1-scale_y) > 0.16:
            #print('s_y: %s'%abs(1-scale_y))
            continue
        if abs(shear) > 12.0:
            #print('shear: %s'%shear)
            continue
        #print((t_x, t_y), rot, shear, (scale_x, scale_y))
        #print('000000000000000000000000000000000000000000000000000000000000000000000000000000')
        
        # translate all points of second
        #dst_corrected_tmp = t.T.dot(M.T).T[:2]
        #print(dst_corrected_tmp)
        dst_corrected_tmp = matrix_transform(dst.T, M).T
        #print(dst_corrected_tmp)

        # get matches
        #src_matches, matches = match_point_clouds(src, dst_corrected_tmp, search_radius=search_radius)
        matches, second_matches = matcher.calc(dst_corrected_tmp)
        # calculate the result

        # use the result if better
        if len(matches) > result:
            #print('(tx, ty), rot, shear, (sx, sy)')
            #print((t_x, t_y), rot, shear, (scale_x, scale_y))
            #log.debug('Affine Matrix:\n%s\n%s'%(result_tmp, M))
            #log.debug('%s'%(tr.params))
            #log.debug('translation, rotation, shear, scale')
            #log.debug('(%s, %s), %s, %s, (%s, %s)'%(t_x, t_y, rot, shear, scale_x, scale_y))
            result = len(matches)
            dst_corrected = dst_corrected_tmp
            dst_matching_points = matches
            src_matching_points = second_matches
            transform = M
            ref_ids = c

    return dst_corrected, (dst_matching_points, src_matching_points), transform, ref_ids, result


def num_nearest(pc, p, num):
    '''Get `num` nearest points from point `p` from point-cloud `pc`
    '''
    pc_c = pc[0] + 1j*pc[1]
    p_c = p[0] + 1j*p[1]
    return numpy.argsort(numpy.abs(pc_c - p_c))[:num]


def initial_points(src, dst):
    '''
    Calculate the points to be used for estimating the transformation of `src` to `dst`
    This is a self-made approach explained below.
    '''
    
    # evaluate 4 init points
    #  +--------------+-------------+ ymax
    #  |              |             |
    #  |     X        |      X      |
    #  |   3          |     4       |
    #  +--------------+-------------+ (ymin+ymax)/2
    #  |              |             |
    #  |     X        |      X      |
    #  |   1          |     2       |
    #  +--------------+-------------+ ymin
    #  xmin  |     (xmin+xmax)/2    xmax
    #        |
    #        xmin + (xmin+xmax)/2
    #        --------------------  -->  (3*xmin + xmax)/4
    #                2
    
    points =  numpy.hstack([src, dst])
    
    # TODO check selection of points
    init_min = (3*numpy.min(points, axis=1) + numpy.max(points, axis=1))/4.
    init_max = (numpy.min(points, axis=1) + 3*numpy.max(points  , axis=1))/4.
    init_points = numpy.array([[init_min[0], init_max[0], init_max[0], init_min[0]], 
                               [init_min[1], init_min[1], init_max[1], init_max[1]]])

    NUM_TEST_POINTS = 3#3 TODO
    #p_combinations = []
    #for p in init_points.T:
    #    p_combinations.append(list(product(num_nearest(src, p, NUM_TEST_POINTS).tolist(), 
    #                                       num_nearest(dst, p, NUM_TEST_POINTS).tolist())))
    p_combinations = [list(product(num_nearest(src, p, NUM_TEST_POINTS).tolist(), \
                                   num_nearest(dst, p, NUM_TEST_POINTS).tolist())) for p in init_points.T]

    combs = numpy.array(list(product(*p_combinations)))
    return combs




def initial_points_3(src, dst):
    '''
    Calculate the points to be used for estimating the transformation of `src` to `dst`
    This is a self-made approach explained below.
    '''
    
    # evaluate 3 init points
    #  +----------------------------+ ymax
    #  |         \                  |
    #  |          \                 |
    #  |           O------\         |
    #  |         /  \ r /  \        |
    #  |        /    \ /    |       |
    #  |     X |    P +-----O-------+ (ymin+ymax)/2
    #  |     2  \    /      |       |
    #  |         \  /      /  X     |
    #  |           O ---- /   3     |
    #  |          /                 |
    #  |         /                  |
    #  |        /                   |
    #  +----------------------------+ ymin
    #  xmin                         xmax
    #
    # width = (xmax + xmin) / 2
    # height = (ymax + ymin) / 2
    # r = width/4
    # P = center
    points = numpy.hstack([src, dst])
    P = complex(*(numpy.max(points, axis=1) + numpy.min(points, axis=1))/2)
    r = numpy.ptp(points, axis=1)[0]/4
    x1 = P + rect(r, 0)
    x2 = P + rect(r, 2*numpy.pi/3) 
    x3 = P + rect(r, -2*numpy.pi/3) 
    init_points = numpy.array([[x1.real, x2.real, x3.real], #x
                               [x1.imag, x2.imag, x3.imag]])#y

    NUM_TEST_POINTS = 3# TODO
    p_combinations = []
    for p in init_points.T:
        src_n = num_nearest(src, p, NUM_TEST_POINTS)
        dst_n = num_nearest(dst, p, NUM_TEST_POINTS)
        #print(src_n, dst_n)
        p_combinations.append(list(product(src_n.tolist(), 
                                           dst_n.tolist())))
    #p_combinations = [list(product(num_nearest(src, p, NUM_TEST_POINTS).tolist(), \
    #                                           num_nearest(dst, p, NUM_TEST_POINTS).tolist())) for p in init_points.T]

    combs = numpy.array(list(product(*p_combinations)))
    return combs