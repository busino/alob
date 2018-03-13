'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
import numpy

from django.views import generic

from image.models import Image


class MainView(generic.TemplateView):
    
    template_name = 'main.html'
    
    def get_context_data(self, **kwargs):
        c = generic.TemplateView.get_context_data(self, **kwargs)
        images = list(Image.objects.filter(disabled=False).values_list('id', flat=True))
        numpy.random.shuffle(images)
        
        c['images'] = images[:48]
        return c
    
    def get(self, request, *args, **kwargs):
        return generic.TemplateView.get(self, request, *args, **kwargs)