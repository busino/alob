'''
Alob Project
2016 -2018
Author(s): R.Walker

'''
import os
import sys
import logging

import numpy

log = logging.getLogger(__name__)


def preprocessing():

    from image.models import Image
    from pair.models import Pair

    log.info('Preprocessing.')
    
    # images
    images = {}
    image_ids = []
    for image in Image.objects.filter(is_labeled=True, disabled=False):
        images[str(image.pk)] = image.pc_recarr()
        image_ids.append(image.pk)

    log.info('{} images selected.'.format(len(image_ids)))

    numpy.savez('images.npz', **images)

    #
    # Calculate some statistics
    #
    xl, yl = [], []
    for _,image in images.items():
        xl.extend(image['x'][4:])
        yl.extend(image['y'][4:])

    xa = numpy.array(xl)
    ya = numpy.array(yl)
    
    log.info('X min: {}, max: {}, mean: {}'.format(xa.min(), xa.max(), xa.mean()))
    log.info('Y min: {}, max: {}, mean: {}'.format(ya.min(), ya.max(), ya.mean()))
    
    #
    # generate the pairs
    #
    cols = ['id', 'first_id', 'second_id', 'match']
    pairs = Pair.objects\
                .filter(first_id__in=image_ids)\
                .filter(second_id__in=image_ids)\
                .filter(disabled_for_training=False) \
                .values_list(*cols)

    log.info('{} pairs'.format(len(pairs)))

    pairs_arr = numpy.core.records.array(list(pairs), names=cols)
    numpy.save('pairs.npy', pairs_arr)
    
    
if __name__ == '__main__':
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    
    sys.path.append(os.path.abspath('../../../alob_django/'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alob_django.settings'
    
    import django
    
    log.info('Setup django')
    
    django.setup()
    
    log.info('-done')

    preprocessing()
    