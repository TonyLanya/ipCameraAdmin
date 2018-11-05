from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
from .models import Cameras, Emails, Users, Properties, Agents
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import re

from app.forms import EmailForm

def index(request):
    # context = {}
    # template = loader.get_template('app/index.html')
    # return HttpResponse(template.render(context, request))
    if request.user.is_superuser:
        return HttpResponseRedirect("/ipcameras")
    else:
        return HttpResponseRedirect("/monitor")


def gentella_html(request):
    context = {}
    # The template to be loaded as per gentelella.
    # All resource paths for gentelella end in .html.

    # Pick out the html file name from the url. And load that template.
    load_template = request.path.split('/')[-1]
    template = loader.get_template('app/' + load_template)
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def ipcamera_html(request):
    context = {}
    template = loader.get_template('app/ipcameras.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def monitor_html(request):
    context = {}
    template = loader.get_template('app/monitor.html')
    return HttpResponse(template.render(context, request))

def login_html(request):
    next = request.GET.get('next')
    context = {"next" : next}
    template = loader.get_template('app/login.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def users_html(request):
    context = {}
    template = loader.get_template('app/users.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def properties_html(request):
    context = {}
    template = loader.get_template('app/properties.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='/login')
def agents_html(request):
    context = {}
    template = loader.get_template('app/agents.html')
    return HttpResponse(template.render(context, request))

def cameras_asJson(request):
    prop_id = request.GET.get("prop_id")
    if prop_id:
        object_list = Cameras.objects.filter(property_id=prop_id)
    else:
        object_list = Cameras.objects.all()
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

def users_asJson(request):
    object_list = Users.objects.all()
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

def properties_asJson(request):
    object_list = Properties.objects.all()
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

def agents_asJson(request):
    object_list = Agents.objects.all()
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

def get_serial(text):
    try:
        found = re.search('Alarm Device Name: (.+?) ', text).group(1)
    except AttributeError:
        # AAA, ZZZ not found in the original string
        found = '' # apply your error handling
    return found
    
@csrf_exempt
def email_receiver(request):
    form = EmailForm(request.POST)
    print(request.POST)
    print(request.POST.get('stripped-text'))
    new_email = Emails()
    new_email.message_id = request.POST.get('Message-Id')
    new_email.subject = request.POST.get('Subject')
    new_email.content = request.POST.get('stripped-text')
    serial = get_serial(re.sub(r"\s+", " ", new_email.content))
    new_email.serial = serial
    cam = Cameras.objects.filter(serial_number=serial)
    if (cam[0].auth_user != ''):
        new_email.notify = True
    new_email.save()
    return HttpResponse("ok")

def get_notify(request):
    if request.GET.get('notify') == '0':
        object_list = Emails.objects.filter(notify=False)
        if (len(object_list) > 0):
            email = object_list[0]
            emails = Emails.objects.filter(message_id=email.message_id)
            emails.update(notify=True)
            serial = email.serial
            cam = Cameras.objects.filter(serial_number=serial)
            cam.update(auth_user = request.user.username)
            json = serializers.serialize('json', cam)
            return HttpResponse(json, content_type='application/json')
        else:
            return HttpResponse('')
    else:
        object_list = Emails.objects.filter(notify=False)
        if (len(object_list) > 0):
            email = object_list[0]
            serial = email.serial
            cam = Cameras.objects.filter(serial_number=serial)
            json = serializers.serialize('json', cam)
            return HttpResponse(json, content_type='application/json')
        else:
            return HttpResponse('')

def remove_notis(request):
    Emails.objects.filter(notify=False).update(notify=True)
    return HttpResponse('')