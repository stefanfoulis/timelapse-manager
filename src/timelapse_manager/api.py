# -*- coding: utf-8 -*-
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


class ImageIntakeSerializer(serializers.Serializer):
    image_url = serializers.CharField(max_length=255, write_only=True)

    def create(self, validated_data):
        image, created = models.Image.objects.create_or_update_from_url(validated_data['image_url'])
        return image


class ImageIntakeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Image.objects.none()
    serializer_class = ImageIntakeSerializer
