# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-28 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_emails_serial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cameras',
            name='online_status',
            field=models.BooleanField(default=True),
        ),
    ]