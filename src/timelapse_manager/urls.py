# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'', views.IndexView.as_view(), name='index'),
]
