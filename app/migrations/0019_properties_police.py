# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-05 14:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_cameras_auth_res'),
    ]

    operations = [
        migrations.AddField(
            model_name='properties',
            name='police',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
