# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from rest_framework import response, routers, serializers, viewsets, views, mixins
from . import models


class CameraSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Camera


class ImageSerializer(serializers.HyperlinkedModelSerializer):
    camera = serializers.ReadOnlyField(source='camera.name')

    class Meta:
        model = models.Image


class ImageViewSet(viewsets.ModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = ImageSerializer


class ImageUrlSerializer(serializers.Serializer):
    image_url = serializers.CharField(max_length=1024, write_only=True)

    def create(self, validated_data):
        images = models.Image.objects.create_or_update_images_from_urls(
            urls=[validated_data['image_url']],
        )
        return images[0]


class ImageIntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Image.objects.none()
    serializer_class = ImageUrlSerializer


class ImageUrlsSerializer(serializers.Serializer):
    images = ImageUrlSerializer(many=True)

    def create(self, validated_data):
        images = models.Image.objects.create_or_update_images_from_urls(
            urls=[img['image_url'] for img in validated_data['images']],
        )
        return {'images': []}


class ImagesIntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Image.objects.none()
    serializer_class = ImageUrlsSerializer
