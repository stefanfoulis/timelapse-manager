# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import tempfile

import datetime
import os
from imageio import imread

from moviepy.editor import CompositeVideoClip, ImageSequenceClip, TextClip, VideoClip


class TimestampedImageSequenceClip(CompositeVideoClip):
    def __init__(self, *args, **kwargs):
        self.clips = []
        self.add_timestamp = kwargs.pop('timestamp', False)
        self.timelapse = ImageSequenceClip(*args, **kwargs)
        self.clips.append(self.timelapse)
        if self.add_timestamp:
            txt_clip = TextClip("MoviePy ROCKS", fontsize=50, color='white')
            self.txt_clip = txt_clip.set_pos('center').set_duration(5)
            self.clips.append(self.txt_clip)
        super(TimestampedImageSequenceClip, self).__init__(self.clips)


class ImageQuerysetClip(VideoClip):
    """
    A VideoClip made from a series of images. Dommain specific to the timelapse-manager django app.
    Inspired by moviepy.editor.ImageSequenceClip
    """
    def __init__(self, qs, size, duration):
        VideoClip.__init__(self, duration=duration)
        self.sequence = qs.iterator()
        self.size = size
        print('has {} images'.format(qs.count()))

    def make_frame(self, t):
        """
        t is a numpy.Float64 representing how many seconds into the video we
        are.
        :param t:
        :return:
        """
        image = self.sequence.next()
        image_file = image.get_file_for_size(size='{}x{}'.format(*self.size))
        print('making frame t={} ({})) with {}'.format(
            t, type(t), image_file.name))
        return imread(uri=image_file)[:,:,:3]


def render_video(queryset=None):
    from .models import Image
    if queryset is None:
        queryset = Image.objects.filter(
            shot_at__gte=datetime.datetime(2016, 4, 23, 11, 0),
            shot_at__lte=datetime.datetime(2016, 4, 23, 12, 0),
        )
    video = ImageQuerysetClip(queryset, size=(160, 120), duration=10)
    try:
        os.makedirs('/data/tmp')
    except:
        pass
    outdir = tempfile.mkdtemp(dir='/data/tmp')
    # outfile = os.path.join(outdir, 'video.mp4')
    # outfile = os.path.join(outdir, 'video.webm')
    outfile = os.path.join(outdir, 'video.gif')
    print('writing to outfile: {}'.format(outfile))
    # video.write_videofile(outfile, audio=False, fps=5)
    video.write_gif(outfile, fps=5)
    # FIXME: must cleanup the temporary file at some point (after saving to
    #        django storage)
    return outfile
