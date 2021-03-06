'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import logging
from time import sleep
import datetime
import json
import subprocess
import os
from itertools import combinations

import joblib

from django.views import generic
from django.db.models import Q
from django.urls.base import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from alob.utils import kill_process_tree, elapsed_human, process_exists

from image.models import Image
from pair.models import Pair

from .models import Prediction
from .apps import PredictionConfig
from .forms import PredictionForm
from contrib.colors import PRED_TYPE_CSS_CLASSES

APP_NAME = PredictionConfig.name
APP_CLASS = Prediction


log = logging.getLogger('alob')


class IndexView(generic.ListView):
  
    model = APP_CLASS
    template_name = '{}/index.html'.format(APP_NAME)


class DetailView(generic.DetailView):
  
    model = APP_CLASS
    template_name = '{}/detail.html'.format(APP_NAME)

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        n = Image.objects.filter(pools__in=self.object.pools.all()).count()
        context['num_images'] = n
        num_comb =  int(n*(n-1)/2)
        t = 2.
        num_procs = max(joblib.cpu_count()-1, 1)
        t = num_comb * t / num_procs 
        context['num_combinations'] = num_comb
        context['num_procs'] = num_procs
        context['approx_calc_time'] = elapsed_human(t)
        if self.object.status == 'running':
            context['time_left'] = datetime.datetime.now()-(self.object.started+datetime.timedelta(seconds=t))
            context['really_running'] = process_exists(self.object.pid)
        
        if self.object.prediction:
            match_ids = json.loads(self.object.prediction)
            matches = Pair.objects.filter(id__in=match_ids)
            num_comb = self.object.num_combinations
            #context['selected_percentage;]'] = self.object.num_selected/num_comb*100
            pool_ids = list(self.object.pools.all().values_list('id', flat=True))
            pairs = Pair.objects.filter(first__pools__in=pool_ids,
                                        second__pools__in=pool_ids)\
                                .order_by('-match')
            context['tp'] = matches.filter(match__in=[1,-1]).count()
            context['fp'] = matches.filter(Q(match=0) | Q(match__isnull=True)).count()
            context['fn'] = pairs.exclude(id__in=match_ids).filter(match__in=[1,-1]).count()
            context['tn'] = pairs.exclude(id__in=match_ids).filter(Q(match=0) | Q(match__isnull=True)).count()
            context['time_used'] = round((self.object.ended - self.object.started).total_seconds())

            data = []            
            for pair in pairs:
                pred = int(pair.pk in match_ids)
                if pred == 0: 
                    if pair.match != 1:
                        continue
                    else:
                        type = 'fn'
                if pred == 1:
                    if pair.match == 1:
                        type = 'tp'
                    else:
                        type = 'fp'
                data.append(dict(pk=pair.pk, match=pair.match, 
                                 type=type, pred=pred, css_class=PRED_TYPE_CSS_CLASSES[type], 
                                 first_name=pair.first.name, second_name=pair.second.name))
            context['data'] = data
            
        return context


class CreateView(generic.CreateView):

    model = APP_CLASS
    template_name = '{}/form.html'.format(APP_NAME)
    form_class = PredictionForm
    
    def get_success_url(self):
        return reverse('prediction:detail',args=(self.object.id,))


class UpdateView(generic.UpdateView):

    model = APP_CLASS
    template_name = '{}/form.html'.format(APP_NAME)
    form_class = PredictionForm
    
    def get_success_url(self):
        return reverse('prediction:detail',args=(self.object.id,))


class DeleteView(generic.DeleteView):
    
    model = APP_CLASS
    success_url = reverse_lazy('{}:index'.format(APP_NAME))
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class GeneratePairView(generic.RedirectView, generic.DetailView):
    
    model = APP_CLASS

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pred_obj = self.object
        
        pool_ids = list(pred_obj.pools.all().values_list('id', flat=True))
    
        image_ids = Image\
                    .objects\
                    .filter(pools__in=pool_ids,\
                            is_labeled=True)\
                    .values_list('pk', flat=True)
    
        log.debug('Images: {}'.format(len(image_ids)))
        
        # Pair generation
        pairs = list(combinations( image_ids,  2))
        num_pairs = len(pairs)
        log.debug('Num Pairs: {}'.format(len(pairs)))
        for f,s in pairs:
            pair = Pair.objects.filter(first_id__in=[f,s], second_id__in=[f,s]).first()
            if pair is None:
                pair = Pair.objects.create(first_id=f, second_id=s)
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))

    def get_redirect_url(self, *args, **kwargs):
        url = reverse_lazy('{}:detail'.format(APP_NAME), kwargs=dict(pk=self.object.pk))
        return url


class ActionView(generic.RedirectView, generic.DetailView):

    model = APP_CLASS

    def get_redirect_url(self, *args, **kwargs):
        url = reverse_lazy('{}:detail'.format(APP_NAME), kwargs=dict(pk=self.object.pk))
        return url

class StartView(ActionView):
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.status == 'running':
            log.debug('Process already started')
        else:
            script = 'predict_script.py'
            cmd = ['python', script, str(self.object.id)] 
            p = subprocess.Popen(cmd, cwd=os.path.abspath(os.path.dirname(os.path.abspath(__file__))),
                                 stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)    
            sleep(4)
            # check if process has returncode
            if p.returncode:
                msg = 'Failed to start subprocess for detection!\n%s'%cmd
            else:
                msg = 'Detection subprocess started!\n%s'%cmd
    
            log.debug(msg)
        return generic.RedirectView.get(self, request, *args, **kwargs)


class StopView(ActionView):
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        pid = self.object.pid
        try:
            kill_process_tree(pid=pid)
            status = 'stopped'
        except:
            status = 'created'
        self.object.status = status
        self.object.save()
        return generic.RedirectView.get(self, request, *args, **kwargs)
