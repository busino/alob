import sys
from time import clock
import logging

import numpy
import pandas

from alob.ml.classifier import AlobPairClassifier


log = logging.getLogger(__name__)
SEARCH_RADIUS = 0.17


def extract_features():
    

    log.info('Extract features')
    
    t0 = clock()


    log.info('Load data')

    images = numpy.load('images.npz')
    pairs = numpy.load('pairs.npy')

    pairs = pairs[:20]# TODO

    image_ids, images = zip(*images.iteritems())
    image_ids = numpy.array(image_ids).astype(numpy.int64)
    images = dict(zip(image_ids, images))

    log.debug('Images: {}'.format(len(images)))
    log.debug('Pairs: {}'.format(len(pairs)))

    log.info('Extract features')

    classifier = AlobPairClassifier(search_radius=SEARCH_RADIUS, 
                                    filename='alob_pair_classifier.pkl')
    
    features = classifier.extract_features(images, pairs[['first_id', 'second_id']].tolist())

    df = pandas.DataFrame(features)
    features_arr = df.to_records(index=False)

    log.info('Store features')
    numpy.save('features.npy', features_arr)
    df.to_pickle('features_df.pkl')

    log.info('Store labels')
    labels = pairs['match']
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
