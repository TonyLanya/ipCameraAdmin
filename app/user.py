from django.http import HttpResponse
from .models import Users
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_new(request):
    new_user = Users()
    new_user.name = request.POST.get('name')
    new_user.phoneno = request.POST.get('phoneno')
    new_user.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")