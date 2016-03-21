# -*- coding: utf-8 -*-
import os


def upload_to_thumbnail(instance, filename, size=None):
    original_path = instance.original.name
    original_name = os.path.basename(original_path)
    return 'timelapse/overview/{size}/{day}/{filename}'.format(
        size=size,
        day=original_name[:10],
        filename=original_name,
    )


# upload_to_thumbnail_160x120 = partial(storage.upload_to_thumbnail, size='160x120')
