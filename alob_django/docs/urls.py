'''
Alob Project
2017
Author(s): R.Walker

'''
from django.conf.urls import url
from .views import ServeDocView, DocsRootView


urlpatterns = [
    url(r'^$', DocsRootView.as_view(), name='index'),
    url(r'^(?P<path>.*)$', ServeDocView.as_view(), name='site'),
]