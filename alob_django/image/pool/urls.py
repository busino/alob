'''
Alob Project
2016
Author(s): R.Walker

'''
from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.ListView.as_view(), name='index'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteView.as_view(), name='delete'),
    # Start labeling
    url(r'^(?P<pk>[0-9]+)/label/$', views.LabelView.as_view(), name='label'),
    #
    url(r'^(?P<pk>[0-9]+)/images/$', views.ImagesView.as_view(), name='images'),
    url(r'^(?P<pk>[0-9]+)/pairs/$', views.PairsView.as_view(), name='pairs'),

]


