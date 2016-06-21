# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import django_filters
import graphene
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters import FilterSet
from graphene import relay
from graphql_relay import from_global_id

from graphene.contrib.django.filter import DjangoFilterConnectionField

from graphene.contrib.django.types import DjangoNode

from . import models
from django.contrib.auth import models as auth_models


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
