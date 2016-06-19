# -*- coding: utf-8 -*-
import os
from getenv import env

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-celery',
    # </INSTALLED_ADDONS>
]

import aldryn_addons.settings
aldryn_addons.settings.load(locals())

# all django settings can be altered here

INSTALLED_APPS.extend([
    # add you project specific apps here
    'timelapse_manager',
    'taggit',
    'rest_framework',
    'rest_framework.authtoken',
    'easy_thumbnails',
])

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/usr/bin/optipng -o7 {filename}',
    'gif': '/usr/bin/optipng -o7 {filename}',
    'jpeg': '/usr/bin/jpegoptim {filename}',
}


# disable multi-language support
USE_I18N = False

TIMELAPSE_STORAGE_DSN = env('TIMELAPSE_STORAGE_DSN')
if TIMELAPSE_STORAGE_DSN:
    import timelapse_manager.storage
    locals().update(
        timelapse_manager.storage.parse_storage_url(
            TIMELAPSE_STORAGE_DSN,
            aws_setting_prefix='AWS_TIMELAPSE_',
            storage_setting_name='TIMELAPSE_FILE_STORAGE',
        )
    )
else:
    TIMELAPSE_FILE_STORAGE = 'timelapse_manager.storage.FileSystemTimelapseStorage'


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework.permissions.DjangoModelPermissions',
    ),
    'DEFAULT_THROTTLE_RATES': {
        # 'bucket:retrieve': '2/day',
        # 'bucket:list': {
        #     'burst': '1/second',
        #     'sustained': '5/hour',
        # },
    },
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'PAGE_SIZE': 100,
}


from aldryn_django import storage
for storage_backend in storage.SCHEMES.values():
    if storage_backend == DEFAULT_FILE_STORAGE:
        THUMBNAIL_DEFAULT_STORAGE = storage_backend
        break

LOGGING['loggers']['celery'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
from logging.config import dictConfig
dictConfig(LOGGING)


# react related stuff
STATICFILES_DIRS.insert(
    0,
    os.path.join(BASE_DIR, 'assets')
)
WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats.json')
    }
}
if not DEBUG:
    WEBPACK_LOADER['DEFAULT'].update({
        'BUNDLE_DIR_NAME': 'dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'webpack-stats-prod.json'),
    })
INSTALLED_APPS.append('webpack_loader')
INSTALLED_APPS.append('graphene.contrib.django')
INSTALLED_APPS.append('django_graphiql')
GRAPHENE_SCHEMA='schema'
