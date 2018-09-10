from django.http import HttpResponse
from .models import Emails
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers

def alerts_asJson(request):
    object_list = Emails.objects.all()
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')