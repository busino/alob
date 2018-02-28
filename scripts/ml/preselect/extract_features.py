import logging
from time import clock
import sys

import numpy
import pandas

from alob.ml.selector import Preselect


log = logging.getLogger(__name__)


SEARCH_RADIUS = 0.25


def extract_features():
    
    
    log.info('Extract Features')
    
    search_radius = SEARCH_RADIUS
    
    t0 = clock()

    log.info('Load data')

    images = numpy.load('images.npz')
    pairs = numpy.load('pairs.npy')
    labels = pairs['match']

    pairs = [(v[0], v[1]) for v in pairs[['first_id', 'second_id']].view((int, 2))]

    image_ids, images = zip(*images.iteritems())
    image_ids = numpy.array(image_ids).astype(numpy.int64)
    images = dict(zip(image_ids, images))
    
    #
    #features = []
    #for pair in pairs:
    #    features.append(extract_helper(images[pair.first_id], images[pair.second_id], search_radius))

    log.info('Extract features')

    preselect = Preselect(search_radius=search_radius, filename='preselect_test.pkl')
    features = preselect.extract_features(images, pairs)


    log.info('Store features')

    features_arr = pandas.DataFrame(features).to_records(index=False)
    numpy.save('features.npy', features_arr)

    log.info('Store labels')
    
    labels[labels==None] = 0
    labels[labels==-1] = 1
    labels = labels.astype(numpy.int64, copy=False)
    numpy.save('labels.npy', labels)

    log.info('Extracted {} features'.format(len(features)))
    
    t1 = clock()-t0
    
    log.info('Time per feature: {:0.5f}'.format(t1/len(features)))

    log.info('Time used: {:0.2f}s'.format(t1))


if __name__ == '__main__':
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    extract_features()

