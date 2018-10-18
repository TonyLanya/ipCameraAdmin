from __future__ import unicode_literals

from django.db import models
import uuid
from django.utils import timezone

# Create your models here.

class Cameras(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular camera across whole library')
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    port = models.CharField(max_length=5)
    login = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    video_stream = models.CharField(max_length=50, null=True)
    data_stream = models.CharField(max_length=50, null=True)
    serial_number = models.CharField(max_length=50)
    property_id = models.IntegerField(null=True)
    created_at = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class Emails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular email')
    message_id = models.CharField(max_length=100)
    subject = models.CharField(max_length=250)
    content = models.TextField(blank=True, null=True)
    notify = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular user')
    name = models.CharField(max_length=100)
    phoneno = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

class Properties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular property')
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.IntegerField(null=True)
    country = models.CharField(max_length=250)
    phoneno = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)

class Agents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular agent')
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.IntegerField(null=True)
    country = models.CharField(max_length=250)
    phoneno = models.CharField(max_length=50)
    created_at = models.DateTimeField(default=timezone.now)
