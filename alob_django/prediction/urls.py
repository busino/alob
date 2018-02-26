'''
Alob Project
2016
Author(s): R.Walker

'''
from django.conf.urls import url
from . import views

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
    # Start
    url(r'^(?P<pk>[0-9]+)/start/$', views.StartView.as_view(), name='start'),
    url(r'^(?P<pk>[0-9]+)/stop/$', views.StopView.as_view(), name='stop'),
]


