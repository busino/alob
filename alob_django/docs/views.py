'''
Alob Project
2017
Author(s): R.Walker

'''
import os
import logging

from django.views import generic
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse_lazy

DOCS_SOURCE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'doc', 'source'))

log = logging.getLogger()

APP_NAME = 'docs'


class ServeDocView(generic.TemplateView):
    
    template_name = '{}/base.html'.format(APP_NAME) 

    def get(self, request, path, *args, **kwargs):
        path = path.replace('.', '')
        filename = os.path.join(DOCS_SOURCE_FOLDER, path+'.rst')
        if not os.path.exists(filename):
            return HttpResponseRedirect(redirect_to=reverse_lazy('docs:index'))
        context = self.get_context_data(**kwargs)
        context['rst_content'] = open(filename).read()
        return self.render_to_response(context)


class DocsRootView(generic.TemplateView):
    
    template_name = '{}/index.html'.format(APP_NAME)
    

