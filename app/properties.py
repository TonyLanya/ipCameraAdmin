from django.http import HttpResponse
from .models import Properties, Users, Cameras
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers

@csrf_exempt
def create_new(request):
    new_prop = Properties()
    new_prop.address = request.POST.get('address')
    new_prop.city = request.POST.get('city')
    new_prop.state = request.POST.get('state')
    new_prop.zipcode = request.POST.get('zipcode')
    new_prop.country = request.POST.get('country')
    new_prop.phoneno = request.POST.get('phoneno')
    new_prop.police = request.POST.get('police')
    new_prop.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def get_properties(request):
    pros = Properties.objects.all()
    json = serializers.serialize('json', pros)
    return HttpResponse(json, content_type='application/json')

@csrf_exempt
def get_property(request):
    id = request.POST.get("id")
    prop = Properties.objects.filter(pk=id)
    json = serializers.serialize('json', prop)
    return HttpResponse(json, content_type='application/json')

@csrf_exempt
def update_property(request):
    try:
        id = request.POST.get("id")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        zipcode = request.POST.get("zipcode")
        country = request.POST.get("country")
        phoneno = request.POST.get("phoneno")
        police = request.POST.get("police")
        prop = Properties.objects.get(pk=id)
        prop.address = address
        prop.city = city
        prop.state = state
        prop.zipcode = zipcode
        prop.country = country
        prop.phoneno = phoneno
        prop.police = police
        prop.save()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def remove_property(request):
    try:
        id = request.POST.get("id")
        users = Users.objects.filter(property_id=id)
        if len(users) > 0:
            return HttpResponse(json.dumps({'status' : "failed", 'msg' : "Please remove users who assigned with this property first."}), content_type="application/json")
        cams = Cameras.objects.filter(property_id=id)
        if len(cams) > 0:
            return HttpResponse(json.dumps({'status' : "failed", 'msg' : "Please remove cameras which assigned with this property first."}), content_type="application/json")
        props = Properties.objects.get(pk=id)
        props.delete()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

        