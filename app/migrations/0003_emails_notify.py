# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-02 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='emails',
            name='notify',
            field=models.BooleanField(default=False),
        ),
    ]
