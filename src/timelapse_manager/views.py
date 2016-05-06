# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.views import generic
from . import models


class TimelapseHome(generic.ListView):
    model = models.Image
    template_name = 'timelapse_manager/home.html'
    context_object_name = 'images'

    def get_queryset(self):
        qs = super(TimelapseHome, self).get_queryset()
        return qs.order_by('-shot_at')[:5]
