# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-10-11 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_cameras_data_stream'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agents',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular agent', primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('zipcode', models.IntegerField(null=True)),
                ('country', models.CharField(max_length=250)),
                ('phoneno', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Properties',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular property', primary_key=True, serialize=False)),
                ('address', models.CharField(max_length=250)),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('zipcode', models.IntegerField(null=True)),
                ('country', models.CharField(max_length=250)),
                ('phoneno', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular user', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('phoneno', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='emails',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='emails',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular email', primary_key=True, serialize=False),
        ),
    ]
