'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import numpy
from skimage.transform import AffineTransform


def transformation_params(M):
    '''Get the translation, rotation, shear and scale from the fransformation matrix `m`

    Args:
        M: tranformation matrix

    Returns:
        translation: t_x, t_y
        rotation: angle
        shear: 
        scale:
    '''
    at = AffineTransform(matrix=M)
    return at.translation, at.rotation*180./numpy.pi, at.shear, at.scale


def affine_matrix_from_points(v0, v1):
    """Return affine transform matrix to match two point clouds.
    
    http://www.lfd.uci.edu/~gohlke/code/transformations.py.html

    v0 and v1 are shape (ndims, \*) arrays of at least ndims non-homogeneous
    coordinates, where ndims is the dimensionality of the coordinate space.

    [15] Multiple View Geometry in Computer Vision. Hartley and Zissermann.
         Cambridge University Press; 2nd Ed. 2004. Chapter 4, Algorithm 4.7, p 130.
     
    By default the algorithm by Hartley and Zissermann [15] is used.
    If usesvd is True, similarity and Euclidean transformation matrices
    are calculated by minimizing the weighted sum of squared deviations
    (RMSD) according to the algorithm by Kabsch [8].

    The returned matrix performs rotation, translation and uniform scaling
    (if specified).

    >>> v0 = [[0, 1031, 1031, 0], [0, 0, 1600, 1600]]
    >>> v1 = [[675, 826, 826, 677], [55, 52, 281, 277]]
    >>> affine_matrix_from_points(v0, v1)
    array([[   0.14549,    0.00062,  675.50008],
           [   0.00048,    0.14094,   53.24971],
           [   0.     ,    0.     ,    1.     ]])
    >>> T = translation_matrix(numpy.random.random(3)-0.5)
    >>> R = random_rotation_matrix(numpy.random.random(3))
    >>> S = scale_matrix(random.random())
    >>> M = concatenate_matrices(T, R, S)
    >>> v0 = (numpy.random.rand(4, 100) - 0.5) * 20
    >>> v0[3] = 1
    >>> v1 = numpy.dot(M, v0)
    >>> v0[:3] += numpy.random.normal(0, 1e-8, 300).reshape(3, -1)
    >>> M = affine_matrix_from_points(v0[:3], v1[:3])
    >>> numpy.allclose(v1, numpy.dot(M, v0))
    True
    """
    v0 = numpy.array(v0, dtype=numpy.float64, copy=True)
    v1 = numpy.array(v1, dtype=numpy.float64, copy=True)

    ndims = v0.shape[0]

    # move centroids to origin
    t0 = -numpy.mean(v0, axis=1)
    M0 = numpy.identity(ndims+1)
    M0[:ndims, ndims] = t0
    v0 += t0.reshape(ndims, 1)
    t1 = -numpy.mean(v1, axis=1)
    M1 = numpy.identity(ndims+1)
    M1[:ndims, ndims] = t1
    v1 += t1.reshape(ndims, 1)

    # Affine transformation
    A = numpy.concatenate((v0, v1), axis=0)
    u, s, vh = numpy.linalg.svd(A.T)
    vh = vh[:ndims].T
    B = vh[:ndims]
    C = vh[ndims:2*ndims]
    t = numpy.dot(C, numpy.linalg.pinv(B))
    t = numpy.concatenate((t, numpy.zeros((ndims, 1))), axis=1)
    M = numpy.vstack((t, ((0.0,)*ndims) + (1.0,)))

    # move centroids back
    M = numpy.dot(numpy.linalg.inv(M1), numpy.dot(M, M0))
    M /= M[ndims, ndims]
    return M
