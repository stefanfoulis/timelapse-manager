# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.files.storage import get_storage_class, FileSystemStorage
from django.utils.functional import LazyObject
from django.utils.text import slugify

from six.moves.urllib import parse
from storages.backends import s3boto
import yurl


SCHEMES = {
    's3': 'timelapse_manager.storage.S3TimelapseStorage',
    'djfs': 'fs.django_storage.DjeeseFSStorage',
    'file': 'timelapse_manager.storage.FileSystemTimelapseStorage',
}

parse.uses_netloc.append('s3')
parse.uses_netloc.append('djfs')


class S3Storage(s3boto.S3BotoStorage):
    aws_setting_prefix = 'AWS_MEDIA_'

    def get_setting(self, name):
        return getattr(settings, '{}{}'.format(self.aws_setting_prefix, name))

    def __init__(self):
        # We cannot use a function call or a partial here. Instead, we have to
        # create a subclass because django tries to recreate a new object by
        # calling the __init__ of the returned object (with no arguments).
        super(S3Storage, self).__init__(
            access_key=self.get_setting('ACCESS_KEY_ID'),
            secret_key=self.get_setting('SECRET_ACCESS_KEY'),
            bucket_name=self.get_setting('STORAGE_BUCKET_NAME'),
            location=self.get_setting('BUCKET_PREFIX'),
            host=self.get_setting('STORAGE_HOST'),
            # Setting an ACL requires us to grant the user the PutObjectAcl
            # permission as well, even if it matches the default bucket ACL.
            # XXX: Ideally we would thus set it to `None`, but due to how
            # easy_thumbnails works internally, that causes thumbnail
            # generation to fail...
            default_acl='public-read',
            querystring_auth=False,
        )

    def listdir(self, path):
        # Implementation stolen from django-s3-storage:
        # https://github.com/etianen/django-s3-storage/blob/e8c1cb2d2b65c8c7047c7851c65af31f091312c9/django_s3_storage/storage.py#L249-L268
        # This one actually works with large buckets.
        path = self._normalize_name(self._clean_name(path))
        # for the bucket.list and logic below name needs to end in /
        # But for the root path "" we leave it as an empty string
        if path and not path.endswith('/'):
            path += '/'

        # Look through the paths, parsing out directories and paths.
        files = set()
        dirs = set()
        for key in self.bucket.list(prefix=path, delimiter="/"):
            key_path = key.name[len(path):]
            if key_path.endswith("/"):
                dirs.add(key_path[:-1])
            else:
                files.add(key_path)
        # All done!
        return list(dirs), list(files)


class S3TimelapseStorage(S3Storage):
    aws_setting_prefix = 'AWS_TIMELAPSE_'


class FileSystemTimelapseStorage(FileSystemStorage):
    def __init__(self, **kwargs):
        location = kwargs.get('location', None)
        if location is None:
            location = os.path.join(settings.MEDIA_ROOT, 'timelapse-images')
        base_url = kwargs.get('base_url', None)
        if base_url is None:
            base_url = settings.MEDIA_URL + 'timelapse-images/'
        kwargs['location'] = location
        kwargs['base_url'] = base_url
        super(FileSystemTimelapseStorage, self).__init__(**kwargs)


class TimelapseStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.TIMELAPSE_FILE_STORAGE)()

timelapse_storage = TimelapseStorage()


def parse_storage_url(url, aws_setting_prefix='AWS_MEDIA_', djeese_setting_prefix='DJEESE_', storage_setting_name='DEFAULT_FILE_STORAGE'):
    settings = {}
    url = parse.urlparse(url)

    scheme = url.scheme.split('+', 1)
    if storage_setting_name:
        settings[storage_setting_name] = SCHEMES[scheme[0]]

    if scheme[0] == 's3':
        os.environ['S3_USE_SIGV4'] = 'True'
        config = {
            'ACCESS_KEY_ID': parse.unquote(url.username or ''),
            'SECRET_ACCESS_KEY': parse.unquote(url.password or ''),
            'STORAGE_BUCKET_NAME': url.hostname.split('.', 1)[0],
            'STORAGE_HOST': url.hostname.split('.', 1)[1],
            'BUCKET_PREFIX': url.path.lstrip('/'),
        }
        media_url = yurl.URL(
            scheme='https',
            host='.'.join([
                config['STORAGE_BUCKET_NAME'],
                config['STORAGE_HOST'],
            ]),
            path=config['BUCKET_PREFIX'],
        )
        settings['MEDIA_URL'] = media_url.as_string()
        settings.update({
            '{}{}'.format(aws_setting_prefix, key): value
            for key, value in config.items()
        })
    elif scheme[0] == 'djfs':
        hostname = ('{}:{}'.format(url.hostname, url.port)
                    if url.port else url.hostname)
        config = {
            'STORAGE_ID': url.username or '',
            'STORAGE_KEY': url.password or '',
            'STORAGE_HOST': parse.urlunparse((
                scheme[1],
                hostname,
                url.path,
                url.params,
                url.query,
                url.fragment,
            )),
        }
        media_url = yurl.URL(
            scheme=scheme[1],
            host=url.hostname,
            path=url.path,
            port=url.port or '',
        )
        settings['MEDIA_URL'] = media_url.as_string()
        settings.update({
            '{}{}'.format(djeese_setting_prefix, key): value
            for key, value in config.items()
        })
    if settings['MEDIA_URL'] and not settings['MEDIA_URL'].endswith('/'):
        # Django (or something else?) silently sets MEDIA_URL to an empty
        # string if it does not end with a '/'
        settings['MEDIA_URL'] = '{}/'.format(settings['MEDIA_URL'])
    return settings


def structured_data_to_image_filename(data):
    return '{shot_at}.{original_name}.{size}.{md5sum}.JPG'.format(**data)


def upload_to_thumbnail(instance, filename, size=None):
    from . import utils
    original_path = instance.original.name
    original_name = os.path.basename(original_path)
    filename = '{shot_at}.{original_name}.{size}.{md5sum}.JPG'.format(
        shot_at=utils.datetime_to_datetimestr(instance.shot_at),
        original_name=instance.name,
        size=size,
        md5sum=getattr(instance, 'scaled_at_{}_md5'.format(size)),
    )
    return '{camera}/{size}/{day}/{filename}'.format(
        size=size,
        day=original_name[:10],
        filename=filename,
        camera=instance.camera.name,
    )


def upload_to_movie_rendering(instance, filename):
    filename = '{name}.{size}.{md5sum}.JPG'.format(
        name=slugify(instance.movie.name),
        size=instance.size,
        md5sum=instance.file_md5,
    )
    return 'movies/{camera}/{size}/{filename}'.format(
        size=instance.size,
        filename=filename,
        camera=instance.movie.camera.name,
    )
