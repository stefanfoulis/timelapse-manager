# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import django_filters
from . import models


class DayFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_type='iexact')
    date_year = django_filters.NumberFilter(name='date', lookup_expr='year')
    date_year__gt = django_filters.NumberFilter(name='date', lookup_expr='year__gt')
    date_year__lt = django_filters.NumberFilter(name='date', lookup_expr='year__lt')

    class Meta:
        model = models.Day
        fields = (
            'date',
        )
        order_by = True


class ImageFilter(django_filters.FilterSet):
    shot_at = django_filters.DateTimeFilter(lookup_type='iexact')

    class Meta:
        model = models.Day
        fields = (
            'shot_at',
        )
        order_by = True
