from django.http import HttpResponse
from .models import Properties
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_new(request):
    new_prop = Properties()
    new_prop.address = request.POST.get('address')
    new_prop.city = request.POST.get('city')
    new_prop.state = request.POST.get('state')
    new_prop.zipcode = request.POST.get('zipcode')
    new_prop.country = request.POST.get('country')
    new_prop.phoneno = request.POST.get('phoneno')
    new_prop.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")