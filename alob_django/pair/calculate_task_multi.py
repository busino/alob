'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import logging
from time import clock
import os
import sys
from joblib import Parallel, delayed

from alob.match import match_images

logging.basicConfig(filename='calculate_task_multi.log', level=logging.DEBUG)


def helper(p_id, first_pcl, second_pcl, search_radius):
    
    logging.info('  match_images for pair id=%s' % p_id)
    _, _, _, _, result = match_images(first_pcl, second_pcl, search_radius)
    logging.info('  result of pair id=%s is %s' % (p_id, result))
    return p_id, result

def dj_helper(p_id, search_radius):
    
    
    sys.path.append(os.path.abspath('../../alob_django'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alob_django.settings'
    
    import django.db
    django.setup()
    
    from pair.models import Pair
        
    pair = Pair.objects.select_related('first', 'second').prefetch_related('first__points', 'second__points').get(pk=p_id)
    _, _, _, _, result = match_images( pair.first.point_cloud(), pair.second.point_cloud(), search_radius, points=4, use_cv=False)
    pair.result = result
    pair.save()

if __name__ == '__main__':



    #
    # Setup
    #

    sys.path.append(os.path.abspath('../../alob_django'))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alob_django.settings'
    
    from django.conf import settings
    import django.db
    django.setup()
    
    #
    # Calculation
    #
    
    t0 = clock()
    
    from pair.models import Pair
    
    pairs = Pair.objects.select_related('first', 'second').prefetch_related('first__points', 'second__points')
    #pairs = list(Pair.objects.select_related('first', 'second').filter(first__date=F('second__date')).values_list('id', flat=True).order_by('-result')[15000:])
    #pairs = Pair.objects.values_list('id', flat=True)

    django.db.connections.close_all()
    
    if False:
        n_jobs = -2
        logging.debug('Using %s jobs in parallel.' % n_jobs)
        results = Parallel(n_jobs=n_jobs, verbose=51)(delayed(dj_helper)(p_id, 3) for p_id in pairs)    
        
    else:
        
        logging.info("Calculate %s pairs." % pairs.count())
    
        p_data = [(pair.id, pair.first.point_cloud(), pair.second.point_cloud()) for pair in pairs]
        
        n_jobs = -2
        logging.debug('Using %s jobs in parallel.' % n_jobs)
        search_radius = settings.SEARCH_RADIUS
        results = Parallel(n_jobs=n_jobs, verbose=51)(delayed(helper)(p_id, first_pcl, second_pcl, search_radius) for (p_id, first_pcl, second_pcl) in p_data)    
    
        logging.debug('Calculation finished.')
        
        #
        # Update results
        #
        django.db.connections.close_all()
        import django.db
        django.setup()
        
        [Pair.objects.filter(pk=pid).update(result=res) for pid, res in results]

    logging.debug('Update of result values in Database finished.')
    logging.info('Time used: %ss' % (clock()-t0))   

