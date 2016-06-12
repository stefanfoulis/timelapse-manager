# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import graphene
from django.core.exceptions import ValidationError
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


class Image(DjangoNode):
    class Meta:
        model = models.Image

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

    @graphene.resolve_only_args
    def resolve_images(self, first=None):
        first = first or 10
        return models.Image.objects.all().order_by('-shot_at')[:first]


class Query(graphene.ObjectType):
    image = relay.NodeField(Image)
    all_images = DjangoFilterConnectionField(Image)

    viewer = graphene.Field(User)

    @graphene.with_context
    def resolve_viewer(self, args, context, info):
        if context.user.is_anonymous():
            return None
        return User(context.user)
