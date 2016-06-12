# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
import timelapse_manager.views

urlpatterns = [
    # add your own patterns here
    url(r'^api/', include('timelapse_manager.api_urls')),
    url(r'^tl/', include('timelapse_manager.urls')),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
) + [
    url(r'', timelapse_manager.views.IndexView.as_view(), name='index'),
]
