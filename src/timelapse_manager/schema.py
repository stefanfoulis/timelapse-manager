# -*- coding: utf-8 -*-
import graphene
from django.db.models import Q
from graphene.relay import Node

from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from . import schema_filters
from . import models
from django.contrib.auth import models as auth_models


def get_url(instance, fieldname):
    field = getattr(instance, fieldname)
    if field:
        return field.url
    return ''


class ImageNode(DjangoObjectType):
    class Meta:
        model = models.Image
        interfaces = (Node,)

    original_url = graphene.String(source='original')
    scaled_at_160x120_url = graphene.String(source='scaled_at_160x120')
    scaled_at_320x240_url = graphene.String(source='scaled_at_320x240')
    scaled_at_640x480_url = graphene.String(source='scaled_at_640x480')

    def resolve_original_url(self, args, context, info):
        return get_url(self, 'original')

    def resolve_scaled_at_160x120_url(self, args, context, info):
        return get_url(self, 'scaled_at_160x120')

    def resolve_scaled_at_320x240_url(self, args, context, info):
        return get_url(self, 'scaled_at_320x240')

    def resolve_scaled_at_640x480_url(self, args, context, info):
        return get_url(self, 'scaled_at_640x480')


class DayNode(DjangoObjectType):
    class Meta:
        model = models.Day
        interfaces = (Node,)

    images = DjangoFilterConnectionField(ImageNode)
    key_frames = DjangoFilterConnectionField(ImageNode)

    def resolve_images(self, args, context, info):
        return self.images.all()

    def resolve_key_frames(self, args, context, info):
        return self.key_frames.all()


class CameraNode(DjangoObjectType):
    class Meta:
        model = models.Camera
        interfaces = (Node,)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }

    days = DjangoFilterConnectionField(
        DayNode,
        filterset_class=schema_filters.DayFilter,
    )
    images = DjangoFilterConnectionField(
        ImageNode,
        filterset_class=schema_filters.ImageFilter,
    )
    latest_image = graphene.Field(ImageNode)

    @graphene.resolve_only_args
    def resolve_latest_image(self):
        return models.Image.objects.exclude(
            Q(original='') |
            Q(scaled_at_160x120='') |
            Q(scaled_at_320x240='') |
            Q(scaled_at_640x480='')
        ).order_by('-shot_at').first()


class UserNode(DjangoObjectType):
    class Meta:
        model = auth_models.User
        interfaces = (Node,)
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
    images = DjangoFilterConnectionField(ImageNode)
    latest_image = graphene.Field(ImageNode)

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


class Query(graphene.AbstractType):
    image = Node.Field(ImageNode)
    all_images = DjangoFilterConnectionField(
        ImageNode,
        filterset_class=schema_filters.ImageFilter,
    )

    camera = Node.Field(CameraNode)
    all_cameras = DjangoFilterConnectionField(CameraNode)
    default_camera = graphene.Field(CameraNode)

    day = Node.Field(DayNode)
    all_days = DjangoFilterConnectionField(
        DayNode,
        filterset_class=schema_filters.DayFilter,
    )

    viewer = graphene.Field(UserNode)

    def resolve_viewer(self, args, context, info):
        if context.user.is_anonymous():
            return None
        return UserNode(context.user)

    def resolve_default_camera(self, args, context, info):
        return CameraNode(models.Camera.objects.all().first())
