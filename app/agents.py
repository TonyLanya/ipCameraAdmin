from django.http import HttpResponse
from .models import Agents
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def create_new(request):
    new_agent = Agents()
    new_agent.username = request.POST.get('username')
    new_agent.address = request.POST.get('address')
    new_agent.city = request.POST.get('city')
    new_agent.state = request.POST.get('state')
    new_agent.zipcode = request.POST.get('zipcode')
    new_agent.country = request.POST.get('country')
    new_agent.phoneno = request.POST.get('phoneno')
    new_agent.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")