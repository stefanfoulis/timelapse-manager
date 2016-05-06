# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^', views.TimelapseHome.as_view()),
]
