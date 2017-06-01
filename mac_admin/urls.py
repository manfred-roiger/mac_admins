from django.conf.urls import url

from . import views

app_name = 'mac_admin'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^base$', views.base, name='News'),
    url(r'^c2sg$', views.c2sg, name='c2sg'),
    url(r'^select$', views.select, name='select'),
]