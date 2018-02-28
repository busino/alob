import sys
from time import clock
import logging

import numpy

from alob.ml.classifier import AlobPairClassifier
from alob.ml.selector import Preselect


log = logging.getLogger(__name__)
SEARCH_RADIUS = 0.17
PRESELCT_SEARCH_RADIUS = 0.25


def train():
    
    
    log.info('Train')
    
    t0 = clock()
    RANDOM_SEED = 1
    
    #
    # load pre-processed feature data
    #
    log.info('Prepare Data')
    #image_df = pandas.read_pickle(os.path.join(folder, 'image_df.pkl'))
    images = numpy.load('images.npz')
    image_ids, images = zip(*images.iteritems())
    image_ids = numpy.array(image_ids).astype(numpy.int64, copy=False)
    images = dict(zip(image_ids, images))
    
    pairs = numpy.load('pairs.npy')
    
    # TODO
    pairs = pairs[:20]

    #
    # Preselect data    
    #
    log.info('Preselect')
    preselect = Preselect(search_radius=PRESELCT_SEARCH_RADIUS, filename='preselect.pkl')
    res = preselect.predict(images, pairs[['first_id', 'second_id']].tolist())
    
    log.info('Num Pairs: {} Selected: {}'.format(len(res), sum(res)))
    log.info('Time used: {}'.format(clock()-t0))
    
    # convert to bool to be used as index
    res = res.astype(bool, copy=False)

    #
    # Load data for classifier
    #
    log.info('Load labels and features:')
    
    labels = numpy.load('labels.npy')
    features = numpy.load('features.npy')

    log.info('  Labels: {}'.format(len(labels)))
    log.info('  Features: {}'.format(len(labels)))

    #
    # Apply pre selection
    #
    log.info('Apply pre-selection')
    labels = labels[res]
    features = features[res]
    
    log.info('  Labels: {}'.format(len(labels)))
    log.info('  Features: {}'.format(len(labels)))
    
    classifier = AlobPairClassifier(search_radius=SEARCH_RADIUS, filename='alob_pair_classifier.pkl')

    #
    # Randomize the labels and features
    #
    numpy.random.seed(RANDOM_SEED)

    selection = numpy.random.permutation(len(labels))
    
    labels = labels[selection]
    features = features[selection]
    
    # make sure to have 50% of matches in train
    selection = numpy.argsort(-labels)
    NUM_SAMPLES = 18# TODO
    labels = labels[selection[:NUM_SAMPLES]]
    features = features[selection[:NUM_SAMPLES]]
    
    test_labels = labels
    test_features = features
    
    log.info('Predict')
    predictions = classifier.predict(features=test_features.tolist())
    
    log.info('Score')
    score = classifier.score(test_labels, predictions)
    
    log.info(score)


if __name__ == '__main__':
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    train()
