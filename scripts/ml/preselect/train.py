'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import sys
from time import clock
import logging

import numpy

from alob.ml.selector import Preselect


log = logging.getLogger(__name__)
SEARCH_RADIUS = 0.25


def train():

    t0 = clock()

    log.info('Train')
    
    log.info('Load data')

    features = numpy.load('features.npy')
    features = features.view((numpy.float, len(features.dtype.names))).copy()
    labels = numpy.load('labels.npy')
    
    search_radius = SEARCH_RADIUS
    
    log.info('Train')

    preselect = Preselect(search_radius=search_radius, filename='alob_pair_preselect.pkl')
    
    preselect.fit(features=features, labels=labels)

    log.info('Save')
    
    preselect.save()
    
    log.debug('Store Preselct to: {}'.format(preselect.filename))

    log.info('Time used: {:0.2f}s'.format(clock()-t0))


if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    
    train()
