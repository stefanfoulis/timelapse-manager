# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 16:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelapse_manager', '0007_auto_20160606_1643'),
    ]

    operations = [
        migrations.AddField(
            model_name='movierendering',
            name='duration',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
