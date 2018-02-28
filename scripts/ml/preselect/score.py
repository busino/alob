import sys
from time import clock
import logging

import numpy

from alob.ml.selector import Preselect


log = logging.getLogger()
SEARCH_RADIUS = 0.25

def score():
    
    
    t0 = clock()

    log.info('Prepare Data')
    
    features = numpy.load('features.npy')
    features = features.view((numpy.float, len(features.dtype.names))).copy()
    labels = numpy.load('labels.npy')

    log.info('Predict')
    search_radius = SEARCH_RADIUS

    preselect = Preselect(search_radius=search_radius, filename='alob_pair_preselect.pkl')

    res = preselect.predict(features=features)

    log.info('Score')

    score = preselect.score(labels, res)

    log.info(score)
    
    log.info('Time used: {:0.2f}s'.format(clock()-t0))


if __name__ == '__main__':
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    
    score()
