'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from django.conf.urls import url
from .views import ServeDocView, DocsRootView

app_name = 'docs'

urlpatterns = [
    url(r'^$', DocsRootView.as_view(), name='index'),
    url(r'^(?P<path>.*)$', ServeDocView.as_view(), name='site'),
]