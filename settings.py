# -*- coding: utf-8 -*-

INSTALLED_ADDONS = [
    # <INSTALLED_ADDONS>  # Warning: text inside the INSTALLED_ADDONS tags is auto-generated. Manual changes will be overwritten.
    'aldryn-addons',
    'aldryn-django',
    'aldryn-sso',
    'aldryn-django-cms',
    'aldryn-devsync',
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
])

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/usr/bin/optipng -o7 {filename}',
    'gif': '/usr/bin/optipng -o7 {filename}',
    'jpeg': '/usr/bin/jpegoptim {filename}',
}


# disable multi-language support
USE_I18N = False
