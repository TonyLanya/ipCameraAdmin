# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-11-05 14:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_users_registered'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameras',
            name='auth_res',
            field=models.CharField(max_length=50, null=True),
        ),
    ]