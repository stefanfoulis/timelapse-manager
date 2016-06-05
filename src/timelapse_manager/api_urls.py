# -*- coding: utf-8 -*-
from django.conf.urls import include, url

from rest_framework import routers

from . import api


router = routers.DefaultRouter()
router.register('images', api.ImageViewSet)
router.register('image-intake', api.ImageIntakeViewSet, base_name='')
router.register('images-intake', api.ImagesIntakeViewSet, base_name='')


urlpatterns = [
    # The currently active API version (without namespace). When resolving URLs
    # and no request object is available to provide an API version, URLs will
    # be resolved against this API version.
    url(r'^v1/', include(router.urls)),

    # Other API versions can be added here. When a given API version has to be
    # promoted to be the current one, it will be enough to change the URL in
    # the pattern above.
    #
    #     url(r'^services/v2/', include(router.urls, namespace='v2')),
    #
    url(r'^v1/', include(router.urls, namespace='v1')),

    # Authentication views provided by DRF.
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
