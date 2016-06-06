# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import dateparser
import datetime

from yurl import URL

from timelapse_manager.storage import timelapse_storage


def datetime_from_filename(filename):
    if all(filename[idx] == '-' for idx in (4, 7)):
        datestr = filename[0:10]
    else:
        return None
    if all(filename[idx] in ('-', ':') for idx in (13, 16)):
        timestr = filename[11:19].replace('-', ':')
    else:
        timestr = ''
    datetimestr = '{} {}'.format(datestr, timestr)
    return dateparser.parse(datetimestr)


def original_filename_from_filename(filename, include_extension=False):
    # old format: 2016-05-03_00-02-59_A_G0070289.JPG
    # new format: 2016-05-03_00-02-59.A_G0070289.original.6c227c09a043c0e30a86a61ddd445734.JPG

    # remove the date and time
    filename = filename[20:]
    # remove '.' seperated stuff in the middle (size and checksum with new format)
    split = filename.split('.')
    if include_extension:
        return '{}.{}'.format(split[0], split[-1])
    else:
        return split[0]


def md5sum_from_filename(filename):
    return filename.split('.')[-2]


def daterange(start_on, end_on):
    day_count = (end_on - start_on).days
    for day_num in range(0, day_count+1):
        yield start_on + datetime.timedelta(days=day_num)


def normalize_image_url(url):
    """
    takes an s3 url or relative url and returns the part that is saved in the
    database (relative to the storage root).
    """
    if url.startswith('http://') or url.startswith('https://'):
        url = URL(url).path
        bucket = '/{}/'.format(timelapse_storage.bucket_name)
        if url.startswith(bucket):
            url = url[len(bucket):]
        if url.startswith(timelapse_storage.location):
            url = url[len(timelapse_storage.location):]
    if hasattr(timelapse_storage, 'base_url') and url.startswith(timelapse_storage.base_url):
        url = url[len(timelapse_storage.base_url):]
    if url.startswith('/'):
        url = url[1:]
    return url


def image_url_to_structured_data(url):
    path = normalize_image_url(url)
    camera_name, size_name, day_name, filename = path.split('/')
    md5sum = md5sum_from_filename(filename=filename)
    shot_at = datetime_from_filename(filename)
    name = original_filename_from_filename(filename)
    return dict(
        url=url,
        path=path,
        camera_name=camera_name,
        size_name=size_name,
        day_name=day_name,
        filename=filename,
        shot_at=shot_at,
        name=name,
        md5sum=md5sum,
    )


def datetime_to_datetimestr(dt):
    return dt.strftime('%Y-%m-%d'), dt.strftime('%Y-%m-%d_%H-%M-%S')
