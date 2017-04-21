# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import django_filters
import graphene
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters import FilterSet
from graphene import relay
from graphql_relay import from_global_id
from graphene.core.types import LazyType

from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from timelapse_manager import schema_filters
from . import models
from django.contrib.auth import models as auth_models


def get_url(instance, fieldname):
    field = getattr(instance, fieldname)
    if field:
        return field.url
    return ''


class Image(DjangoNode):
    class Meta:
        model = models.Image
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'shot_at': ['exact', 'icontains', 'istartswith'],
            'original': ['exact', 'icontains', 'istartswith'],
            'original_md5': ['exact', 'icontains', 'istartswith'],
        }

    original_url = graphene.StringField(source='original')
    scaled_at_160x120_url = graphene.StringField(source='scaled_at_160x120')
    scaled_at_320x240_url = graphene.StringField(source='scaled_at_320x240')
    scaled_at_640x480_url = graphene.StringField(source='scaled_at_640x480')

    @graphene.resolve_only_args
    def resolve_original_url(self):
        return get_url(self.instance, 'original')

    @graphene.resolve_only_args
    def resolve_scaled_at_160x120_url(self):
        return get_url(self.instance, 'scaled_at_160x120')

    @graphene.resolve_only_args
    def resolve_scaled_at_320x240_url(self):
        return get_url(self.instance, 'scaled_at_320x240')

    @graphene.resolve_only_args
    def resolve_scaled_at_640x480_url(self):
        return get_url(self.instance, 'scaled_at_640x480')


class Day(DjangoNode):
    class Meta:
        model = models.Day
        filter_fields = [
            'date',
        ]

    images = DjangoFilterConnectionField(Image)
    key_frames = DjangoFilterConnectionField(Image)

    @graphene.with_context
    def resolve_images(self, args, context, info):
        return self.instance.images.all()

    @graphene.with_context
    def resolve_key_frames(self, args, context, info):
        return self.instance.key_frames.all()


class Camera(DjangoNode):
    class Meta:
        model = models.Camera
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }

    days = DjangoFilterConnectionField(
        Day,
        filterset_class=schema_filters.DayFilter,
    )
    images = DjangoFilterConnectionField(
        Image,
        filterset_class=schema_filters.ImageFilter,
    )
    latest_image = graphene.Field(Image)

    @graphene.resolve_only_args
    def resolve_latest_image(self):
        return models.Image.objects.exclude(
            Q(original='') |
            Q(scaled_at_160x120='') |
            Q(scaled_at_320x240='') |
            Q(scaled_at_640x480='')
        ).order_by('-shot_at').first()


class User(DjangoNode):
    class Meta:
        model = auth_models.User
    only_fields = (
        'username',
        'first_name',
        'last_name',
        'email',
        'images',
    )
    exclude_fields = (
        'password',
    )
    images = DjangoFilterConnectionField(Image)
    latest_image = graphene.Field(Image)

    @graphene.resolve_only_args
    def resolve_images(self, first=None):
        first = first or 10
        return models.Image.objects.all().order_by('-shot_at')[:first]

    @graphene.resolve_only_args
    def resolve_latest_image(self):
        return models.Image.objects.exclude(
            Q(original='') |
            Q(scaled_at_160x120='') |
            Q(scaled_at_320x240='') |
            Q(scaled_at_640x480='')
        ).order_by('-shot_at').first()


class Query(graphene.ObjectType):
    image = relay.NodeField(Image)
    all_images = DjangoFilterConnectionField(Image)

    camera = relay.NodeField(Camera)
    all_cameras = DjangoFilterConnectionField(Camera)
    default_camera = graphene.Field(Camera)

    day = relay.NodeField(Day)
    all_days = DjangoFilterConnectionField(
        Day,
        filterset_class=schema_filters.DayFilter
    )

    viewer = graphene.Field(User)

    @graphene.with_context
    def resolve_viewer(self, args, context, info):
        if context.user.is_anonymous():
            return None
        return User(context.user)

    @graphene.with_context
    def resolve_default_camera(self, args, context, info):
        return Camera(models.Camera.objects.all().first())
