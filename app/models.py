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
    serial_number = models.CharField(max_length=50)
    property_id = models.CharField(max_length=100, null=True)
    online_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    auth_state = models.CharField(max_length=50, default="AUTHORIZING")
    auth_res = models.CharField(max_length=50, null=True)
    auth_user = models.CharField(max_length=50, null=True)
    lastConnection = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.name

class Emails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular email')
    message_id = models.CharField(max_length=100)
    subject = models.CharField(max_length=250)
    content = models.TextField(blank=True, null=True)
    notify = models.BooleanField(default=False)
    serial = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class Users(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular user')
    name = models.CharField(max_length=100)
    phoneno = models.CharField(max_length=50)
    property_id = models.CharField(max_length=100, null=True)
    registered = models.BooleanField(default=False)
    trained_name = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class Properties(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular property')
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.IntegerField(null=True)
    country = models.CharField(max_length=250)
    phoneno = models.CharField(max_length=50)
    police = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField(default=timezone.now)

class Agents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular agent')
    email = models.CharField(max_length=50, null=True)
    username = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    zipcode = models.IntegerField(null=True)
    country = models.CharField(max_length=250)
    phoneno = models.CharField(max_length=50)
    lastConnection = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default="offline")
    created_at = models.DateTimeField(default=timezone.now)
