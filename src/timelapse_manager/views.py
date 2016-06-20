# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'index.html'
