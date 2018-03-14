'''
Alob Project
2016 - 2018
Author(s): R.Walker

'''
from django.conf.urls import url, include

from . import views


urlpatterns = [
    # List
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^csv/$', views.ExportCSV.as_view(), name='csv'),
    url(r'^filter/$', views.FilterView.as_view(), name='filter'),
    # Detail
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # Set Match state
    url(r'^(?P<pk>[0-9]+)/update/$', views.update, name='update'),
    # set comment
    url(r'^(?P<pk>[0-9]+)/comment/$', views.comment, name='comment'),
    # Pair Pools
    url(r'^pool/', include('pair.pool.urls', namespace='pool'))
]


