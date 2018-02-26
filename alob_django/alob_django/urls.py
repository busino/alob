'''
Alob Project
2016
Author(s): R.Walker

'''
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from main import views


urlpatterns =[
    #url(r'^$', lambda x: redirect('/image/')),
    url(r'^$', views.MainView.as_view()),
    url(r'^image/', include('image.urls', namespace='image')),
    url(r'^pair/', include('pair.urls', namespace='pair')),
    url(r'^prediction/', include('prediction.urls', namespace='prediction')),
    url(r'^docs/', include('docs.urls', namespace='docs')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
