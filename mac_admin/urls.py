from django.conf.urls import url

from . import views

app_name = 'mac_admin'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^c2sg$', views.c2sg, name='c2sg'),
    url(r'^select$', views.select, name='select'),
    url(r'^confirm$', views.confirm, name='confirm'),
    url(r'^under_construction$', views.under_construction, name='under_construction'),
    url(r'^result$', views.assign_c2sg, name='assign_c2sg'),
]
