# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from django.contrib import admin
from .models import Camera, Image, Annotation, Day


class AnnotationInlineAdmin(admin.TabularInline):
    model = Annotation


class CameraAdmin(admin.ModelAdmin):
    inlines = (
        AnnotationInlineAdmin,
    )


class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'camera',
        'shot_at',
        'original',
    )
    list_filter = (
        'camera',
        # TODO: filter by has original, has scaled
    )
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


class AnnotationAdmin(admin.ModelAdmin):
    pass


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
    )

    def get_queryset(self, request):
        qs = super(DayAdmin, self).get_queryset(request)
        qs = qs.select_related('cover')

        return qs

    def set_keyframes_action(self, request, queryset):
        for day in queryset:
            day.set_key_frames()

    def create_keyframe_thumbnails_action(self, request, queryset):
        for day in queryset:
            day.create_keyframe_thumbnails()

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

admin.site.register(Camera, CameraAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(Day, DayAdmin)
