# -*- coding: utf-8 -*-
from django.db.models import ImageField
import django_filters
from . import models


class DayFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(lookup_expr='iexact')
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
    class Meta:
        model = models.Image
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'shot_at': ['exact', 'icontains', 'istartswith'],
            'original': ['icontains', 'istartswith'],
            'original_md5': ['exact', 'icontains', 'istartswith'],
        }
        filter_overrides = {
            ImageField: {
                'filter_class': django_filters.CharFilter,
            }
        }
        order_by = True
