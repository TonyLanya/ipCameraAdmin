from django.http import HttpResponse
from .models import Users, Properties
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers
import camera
import numpy as np
import os

### amazon
### /root/ipCameraAdmin/app/static
static_url = "/root/ipCameraAdmin/app/static"

@csrf_exempt
def create_new(request):
    new_user = Users()
    new_user.name = request.POST.get('name')
    new_user.phoneno = request.POST.get('phoneno')
    new_user.property_id = request.POST.get('propid')
    print request.POST.get('propid')
    new_user.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def remove(request):
    try:
        id = request.POST.get("id")
        user = Users.objects.get(pk=id)
        user.delete()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def get_user(request):
    try:
        id = request.POST.get("id")
        user = Users.objects.filter(pk=id)
        propid = user[0].property_id
        ret = {}
        ret["name"] = user[0].name
        ret["phoneno"] = user[0].phoneno
        ret["pk"] = str(user[0].id)
        if propid != None:
            properties = Properties.objects.get(pk=propid)
            ret['prop_name'] = properties.address
        # res = serializers.serialize('json', ret)
        # print type(res)
        # print ret
        ret["prop_id"] = user[0].property_id
        return HttpResponse(json.dumps(ret), content_type='application/json')
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def update_user(request):
    try:
        id = request.POST.get("id")
        name = request.POST.get("name")
        phoneno = request.POST.get("phoneno")
        propid = request.POST.get("propid")
        user = Users.objects.get(pk=id)
        if user.registered == 1:
            if (user.name != name) or (user.property_id != propid) :
                old_path = static_url + "/images/" + user.property_id + "/" + user.name + ".csv"
                new_path = static_url + "/images/" + propid + "/" + name + ".csv"
                os.rename(old_path, new_path)
        user.name = name
        user.phoneno = phoneno
        user.property_id = propid
        user.save()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def register_photo(request):
    try:
        id = request.POST.get("id")
        user = Users.objects.filter(pk=id)
        prop_id = user[0].property_id
        sourceurl = static_url + "/images/" + prop_id + "/" + user[0].name + ".jpg"
        suc, source = camera.get_source(sourceurl)
        if suc == 0:
            return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")
        np.savetxt(static_url + "/images/" + prop_id + "/" + user[0].name + ".csv", source, delimiter=",")
        Users.objects.filter(pk=id).update(registered=True)
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

