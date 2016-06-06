# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import datetime
from django.contrib import admin, messages
from django.utils.encoding import smart_text

from .models import Camera, Image, Day, Tag, TagInfo, Movie, MovieRendering
from . import tasks, utils


class CameraAdmin(admin.ModelAdmin):
    actions = (
        'create_days_for_existing_images_action',
        'create_days_for_oldest_existing_image_until_today_action',
    )

    def create_days_for_existing_images_action(self, request, queryset):
        for camera in queryset:
            days = camera.create_days()
            self.message_user(
                request,
                '{}: created {} days. Now has a total of {} days.'.format(
                    camera,
                    len(days),
                    camera.days.all().count(),
                )
            )

    def create_days_for_oldest_existing_image_until_today_action(self, request, queryset):
        for camera in queryset:
            day_one = camera.images.order_by('shot_at').first()
            if not day_one:
                self.message_user(
                    request,
                    '{}: no existing images!',
                    level=messages.WARNING,
                )
                continue
            days = []
            start_on = day_one.shot_at.date()
            end_on = datetime.date.today()
            for date in utils.daterange(
                start_on=start_on,
                end_on=end_on,
            ):
                day, created = Day.objects.get_or_create(
                    camera=camera,
                    date=date,
                )
                if created:
                    days.append(day)
            self.message_user(
                request,
                '{}: created {} days. Now has a total of {} days. ({} - {})'.format(
                    camera,
                    len(days),
                    camera.days.all().count(),
                    start_on,
                    end_on,
                )
            )

    def discover_images_action(self, request, queryset):
        for camera in queryset:
            tasks.discover_images.delay(camera_id=camera.id)


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'camera',
        'shot_at',
        'original',
        'scaled_at_640x480',
        'scaled_at_320x240',
        'scaled_at_160x120',
    )
    list_filter = (
        'camera',
        # TODO: filter by has original, has scaled
    )
    date_hierarchy = 'shot_at'
    search_fields = (
        'original',
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
        # 'scaled_at_640x480',
    )
    actions = (
        'create_thumbnails_action',
    )

    def create_thumbnails_action(self, request, queryset):
        for image in queryset:
            image.create_thumbnails()


class DayAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'cover_img',
        'keyframes_img',
        'image_count',
    )
    actions = (
        'set_keyframes_action',
        'create_keyframe_thumbnails_action',
        'set_keyframes_and_create_keyframe_thumbnails_action',
        'discover_images_action',
        'discover_images_and_process_action',
    )
    raw_id_fields = (
        'cover',
    )
    fields = (
        'camera',
        'date',
        'cover',
    )
    ordering = (
        '-date',
    )
    date_hierarchy = 'date'

    def get_queryset(self, request):
        qs = super(DayAdmin, self).get_queryset(request)
        qs = qs.select_related('cover')
        qs = qs.prefetch_related('key_frames')
        return qs

    def set_keyframes_action(self, request, queryset):
        for day in queryset:
            day.set_key_frames()

    def create_keyframe_thumbnails_action(self, request, queryset):
        for day in queryset:
            tasks.create_keyframe_thumbnails_on_day.delay(
                day_id=smart_text(day.id))

    def set_keyframes_and_create_keyframe_thumbnails_action(
            self, request, queryset):
        for day in queryset:
            tasks.set_keyframes_on_day.delay(
                day_id=smart_text(day.id),
                create_thumbnails=True,
            )

    def discover_images_action(self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(
                day_id=smart_text(day.id))

    def discover_images_and_process_action(
            self, request, queryset):
        for day in queryset:
            tasks.discover_images_on_day.delay(
                day_id=smart_text(day.id),
                set_keyframes=True,
                create_keyframe_thumbnails=True,
            )

    def cover_img(self, obj):
        image = obj.cover
        if not image:
            return ''
        if image.scaled_at_160x120:
            return '<img src="{}" style="width: 160px; height: 120px" />'.format(
                image.scaled_at_160x120.url)
        else:
            return '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
    cover_img.allow_tags = True

    def keyframes_img(self, obj):
        html_list = []
        for image in obj.key_frames.all().order_by('shot_at'):
            if image.scaled_at_160x120:
                html = '<img src="{}" style="width: 160px; height: 120px" />'.format(
                    image.scaled_at_160x120.url)
            else:
                html = '<div style="display: inline-block; border: 1px dashed gray; width: 160px; height: 120px; text-align: center">thumbnail missing</div>'
            html_list.append(html)
        return "&nbsp;".join(html_list)
    keyframes_img.allow_tags = True


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'start_at',
        'end_at',
        'duration',
        'image_count',
    )
    readonly_fields = (
        'image_count',
        'duration',
    )


class TagInfoAdmin(admin.ModelAdmin):
    pass


class MovieRenderingInline(admin.TabularInline):
    model = MovieRendering
    extra = 0


class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'tags_display',
        'image_count',
    )
    readonly_fields = (
        'tags_display',
        'image_count',
    )
    inlines = (
        MovieRenderingInline,
    )


class MovieRenderingAdmin(admin.ModelAdmin):
    actions = (
        'render_action',
    )
    readonly_fields = (
        'preview_html',
    )

    def render_action(self, request, queryset):
        for obj in queryset:
            tasks.render_movie(
                movie_rendering_id='{}'.format(obj.id)
            )

    def preview_html(self, obj):
        return '''<img src="{}" />'''.format(obj.file.url)
    preview_html.allow_tags = True


admin.site.register(Camera, CameraAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Day, DayAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(TagInfo, TagInfoAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(MovieRendering, MovieRenderingAdmin)
