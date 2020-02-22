'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import sys
import os
import logging
from time import perf_counter
import datetime
from itertools import product, combinations
from collections import OrderedDict

import argparse

import django
import django.db

import pandas
import numpy

from alob.ml.classifier import AlobPairClassifier
from alob.ml.selector import Preselect

log = logging.getLogger('alob')


def main(prediction_id, stats=False):

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    log.debug('Base path: {}'.format(base_path))
    sys.path.append(base_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alob_django.settings'

    django.db.connection.close()
    django.setup()
    
    from django.conf import settings

    log.debug('Django is setup.')

    from image.models import Image, ImagePool, Point
    from pair.models import Pair
    from prediction.models import Prediction
    
    # get the prediction object and set the params
    pred_obj = Prediction.objects.get(pk=prediction_id)

    pred_obj.started = datetime.datetime.now()
    pred_obj.status = 'running'
    pred_obj.pid = os.getpid()
    pred_obj.save()
    
    # dict to store prop values of the prediction object
    props = dict()
    
    # Run the prediction and reset the status if failed
    # use try except here

    try:
    
        pool_ids = list(pred_obj.pools.all().values_list('id', flat=True))
    
        images = OrderedDict([(im.pk, im.pc_recarr()) for im in Image\
                                                           .objects\
                                                           .filter(pools__in=pool_ids,\
                                                                   is_labeled=True)])
    
        image_ids = images.keys()
        log.debug('Images: {}'.format(len(image_ids)))
        
        # Pair generation
        pairs = list(combinations( image_ids,  2))
        num_pairs = len(pairs)
        log.debug('Num Pairs: {}'.format(len(pairs)))
    
        #
        # TODO Preselect
        #
        preselect = Preselect(filename='__default__', search_radius=settings.PRESELECT_SEARCH_RADIUS)
        res = preselect.predict(images, pairs)
        res = numpy.array(res).astype(bool)
        pairs = numpy.array(pairs)[res].tolist()
        log.debug('Selected: {}/{}'.format(len(pairs), num_pairs))
    
        # Predict
        cl = AlobPairClassifier(filename='__default__', search_radius=settings.SEARCH_RADIUS)
        features = cl.extract_features(images, pairs)
        features_df = pandas.DataFrame(features)
        features_df.to_json('features.json')
        log.info('Features extracted.')
        features = features_df.values
        res = cl.predict(images, pairs, features)
        log.info('Predicted.')

        prediction_df = pandas.DataFrame(res)
        prediction_df.to_json('prediction.json')
    
        match_indices = numpy.array(pairs)[numpy.array(res).astype(bool)]
        match_pairs = []
        for f,s in match_indices:
            pair = Pair.objects.filter(first_id__in=[f,s], second_id__in=[f,s]).first()
            if pair is None:
                pair = Pair.objects.create(first_id=f, second_id=s)
            match_pairs.append(pair.id)
    
        if stats:
            db_pairs = Pair.objects.filter(first_id__in=image_ids, 
                                           second_id__in=image_ids).order_by('-match')
            result = []
            for pair in db_pairs:
                result.append(dict(id=pair.id, match=pair.match, prediction=pair.id in match_pairs))
        
            result_df = pandas.DataFrame(result).sort_values(by=['match', 'prediction'])
            result_df.to_json('result.json')
            log.debug('Time used: {}s'.format(perf_counter()-t0))
            log.debug(result_df)
    except Exception as e:
        log.error(str(e))
        props['status'] = 'failed'
    else:
        props['status'] = 'finished'
        props['num_combinations'] = len(pairs)
        props['ended'] = datetime.datetime.now()
        props['prediction'] = match_pairs

    # Update the prediction object
    
    # reopen the database connection because its lost while the long run
    django.db.connection.close()
    django.setup()
    
    pred_obj = Prediction.objects.get(pk=prediction_id)
    for k, v in props.items():
        setattr(pred_obj, k, v)
    pred_obj.save()


if __name__ == '__main__':
    
    fh = logging.FileHandler('predict_script.log')
    log.addHandler(fh)
    log.setLevel(logging.DEBUG)
    log.info('Process pid: {}'.format(os.getpid()))

    t0 = perf_counter()

    parser = argparse.ArgumentParser(description='Predict Pools')
    
    parser.add_argument(dest='prediction', metavar='prediction', type=int,
                        help='Prediction DB id')
    parser.add_argument('-s', '--stats', help='Print Statistics of the run',
                        required=False, action='store_true')

    args = parser.parse_args()

    main(args.prediction, args.stats)

    log.debug('Time used: {:.2f}s'.format(perf_counter()-t0))