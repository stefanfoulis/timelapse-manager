# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import graphene
from django.core.exceptions import ValidationError
from django.db.models import Q
from graphene import relay
from graphql_relay import from_global_id

from graphene.contrib.django.filter import DjangoFilterConnectionField

from graphene.contrib.django.types import DjangoNode

from . import models
from django.contrib.auth import models as auth_models


def get_url(instance, fieldname):
    field = getattr(instance, fieldname)
    if field:
        return field.url
    return ''


class Camera(DjangoNode):
    class Meta:
        model = models.Camera
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }


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

    images = DjangoFilterConnectionField(Image)

    @graphene.with_context
    def resolve_images(self, args, context, info):
        return self.instance.images.all()


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

    day = relay.NodeField(Day)
    all_days = DjangoFilterConnectionField(Day)

    viewer = graphene.Field(User)

    @graphene.with_context
    def resolve_viewer(self, args, context, info):
        if context.user.is_anonymous():
            return None
        return User(context.user)
