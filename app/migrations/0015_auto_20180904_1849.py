# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-09-04 18:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_users_property_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cameras',
            name='data_stream',
        ),
        migrations.RemoveField(
            model_name='cameras',
            name='video_stream',
        ),
    ]