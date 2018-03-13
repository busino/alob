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
    # Detail
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.UpdateView.as_view(), name='update'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.DeleteView.as_view(), name='delete'),
    url(r'^(?P<pk>[0-9]+)/rotate/$', views.RotateView.as_view(), name='rotate'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^filter/$', views.FilterView.as_view(), name='filter'),
    url(r'^(?P<pk>[0-9]+)/label$', views.LabelView.as_view(), name='label'),
    url(r'^import_excel$', views.import_excel, name='import_excel'),
    # Resulting list
    url(r'^result/$', views.ResultView.as_view(), name='result'),
    url(r'^result_cmr/$', views.ResultCmrView.as_view(), name='result_cmr'),
    url(r'^(?P<pk>[0-9]+)/marked_image_jpeg$', views.marked_image_jpeg, name='marked_image_jpeg'),
    url(r'^(?P<pk>[0-9]+)/marked_image_jpeg/(?P<width>[0-9]+)$', views.marked_image_jpeg, name='marked_image_jpeg'),
    url(r'^(?P<pk>[0-9]+)/image_jpeg$', views.image_jpeg, name='image_jpeg'),
    # Update Points
    url(r'^(?P<pk>[0-9]+)/json_update_point$', views.JSONUpdatePointView.as_view(), name='json_update_point'),
    url(r'^point/(?P<pk>[0-9]+)/delete/$', views.DeletePointView.as_view(), name='point_delete'),
    # Delete all points of the image
    url(r'^(?P<pk>[0-9]+)/delete_points/$', views.DeletePointsView.as_view(), name='delete_points'),
    # Image Pools
    url(r'^pool/', include('image.pool.urls', namespace='pool')),
]


