'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from django.conf.urls import url
from . import views

app_name = 'prediction'

urlpatterns = [
    # List
    url(r'^$', views.IndexView.as_view(), name='index'),
    # Detail
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # Create
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateView.as_view(), name='update'),
    # Delete
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteView.as_view(), name='delete'),
    # Generate Pairs
    url(r'^(?P<pk>[0-9]+)/generate_pairs/$', views.GeneratePairView.as_view(), name='generate_pairs'),
    # Start
    url(r'^(?P<pk>[0-9]+)/start/$', views.StartView.as_view(), name='start'),
    url(r'^(?P<pk>[0-9]+)/stop/$', views.StopView.as_view(), name='stop'),
]


