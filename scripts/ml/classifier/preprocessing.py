import os
import sys
from time import clock
import logging

import numpy


log = logging.getLogger(__name__)


def preprocessing():

    log.info('Preprocessing')

    t0 = clock()

    from image.models import Image
    from pair.models import Pair
    
    # images
    images = {}
    image_ids = []
    for image in Image.objects.filter(is_labeled=True, disabled=False):
        images[str(image.pk)] = image.pc_recarr()
        image_ids.append(image.pk)

    numpy.savez('images.npz', **images)
    
    log.info('Extracted {} images'.format(len(image_ids)))
    
    #
    # generate the pairs
    #
    cols = ['id', 'first_id', 'second_id', 'match']
    pairs = Pair.objects\
                .filter(first_id__in=image_ids)\
                .filter(second_id__in=image_ids)\
                .filter(disabled_for_training=False) \
                .values_list(*cols)

    log.info('Extracted {} pairs'.format(len(pairs)))

    pairs_arr = numpy.core.records.array(list(pairs), names=cols)
    numpy.save('pairs.npy', pairs_arr)

    log.info('Time used: {:.3f}s'.format(clock()-t0))


if __name__ == '__main__':
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    
    sys.path.append(os.path.abspath('../../../alob_django/'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alob_django.settings'
    
    import django
    
    django.setup()

    preprocessing()
    
