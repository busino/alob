
from joblib import Parallel, delayed

def p_fv(args, **kwargs):
    return ClassifierAlgo.pair_feature_vec(*args, *kwargs)

def feature_vec(cl, point_cloud_pairs):
    p = Parallel(n_jobs= -1, backend="threading")
    f_values = p(delayed(p_fv)(i) for i in zip([cl]*len(point_cloud_pairs), point_cloud_pairs))    
    