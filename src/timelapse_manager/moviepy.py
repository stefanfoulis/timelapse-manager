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


class FrameQuerysetClip(VideoClip):
    """
    A VideoClip made from a series of images. Dommain specific to the
    timelapse-manager django app.
    Inspired by moviepy.editor.ImageSequenceClip
    """
    def __init__(self, qs, size, fps, duration):
        VideoClip.__init__(self, duration=duration)
        self.frames = {
            frame.number: frame
            for frame in qs
        }
        self.fps = fps
        self.size = [int(value) for value in size.split('x')]
        self.size_str = size
        print('has {} frames'.format(qs.count()))

    def make_frame(self, t):
        """
        t is a numpy.Float64 representing how many seconds into the video we
        are.
        :param t:
        :return:
        """
        frame_number = int(t * self.fps)
        frame = self.frames[frame_number]
        image_file = frame.image.get_file_for_size(size=self.size_str)
        if not image_file:
            frame.image.create_thumbnails()
        image_file = frame.image.get_file_for_size(size=self.size_str)
        print('making frame t={} ({})) with {}'.format(
            t, type(t), image_file.name))
        return imread(uri=image_file)[:, :, :3]


def render_video(queryset, size, format, fps, duration):
    video = FrameQuerysetClip(queryset, size=size, fps=fps, duration=duration)
    try:
        os.makedirs('/data/tmp')
    except:
        pass
    outdir = tempfile.mkdtemp(dir='/data/tmp')
    outfile = os.path.join(outdir, 'video.{}'.format(format))
    print('writing to outfile: {}'.format(outfile))
    if format == 'gif':
        video.write_gif(outfile)
    else:
        video.write_videofile(outfile, audio=False)
    # FIXME: must cleanup the temporary file at some point (after saving to
    #        django storage)
    return outfile
