from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,StreamingHttpResponse
from django.core import serializers
from .models import Cameras, Emails
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators import gzip
import json
import datetime
import cv2 
import time
import io
import openface
import numpy as np
from threading import Thread

@csrf_exempt
def create_new(request):
    new_camera = Cameras()
    new_camera.name = request.POST.get('name')
    new_camera.address = request.POST.get('address')
    new_camera.port = request.POST.get('port')
    new_camera.video_stream = request.POST.get('vstream')
    new_camera.data_stream = request.POST.get('dstream')
    new_camera.login = request.POST.get('login')
    new_camera.password = request.POST.get('password')
    new_camera.serial_number = request.POST.get('serialnumber')
    new_camera.property_id = request.POST.get('propertyid')
    new_camera.save()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

class VideoCamera(object):
    def __init__(self, rtsp_url):
        self.video = cv2.VideoCapture(rtsp_url)
        self.video_status = 1
    def __del__(self):
        self.video.release()

    def get_frame(self):
        if (self.video.isOpened() == False):
            self.video_status = 0
            return None
        ret,image = self.video.read()
        if ret == False:
            self.video_status = 0
            return None
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()
    def get_status(self):
        return self.video_status

def gen(camera):
    while camera.get_status():
        frame = camera.get_frame()
        if frame != None:
            yield(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(5)

@gzip.gzip_page
@csrf_exempt
def video_feed(request):
    try:
        rtsp = request.GET.get('streamUrl')
        rtsp = rtsp + "&subtype=1"
        ### amazon
        ### rtsp
        return StreamingHttpResponse(gen(VideoCamera("rtsp://admin:patrol88@166.241.170.18:1111/cam/playback?channel=1&starttime=2018_11_01_02_40_00&endtime=2018_11_01_02_41_59")),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")


#### OPENFCACE FUNCTION
def getRep(align, net, bgrImg, imgDim, verbose = None):
    start = time.time()
    if bgrImg is None:
        return "Unable to load image"
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    if verbose:
        print("  + Original size: {}".format(rgbImg.shape))

    start = time.time()
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        return "Unable to find face"
    if verbose:
        print("  + Face detection took {} seconds.".format(time.time() - start))

    start = time.time()
    alignedFace = align.align(imgDim, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        return "Unable to align"
    if verbose:
        print("  + Face alignment took {} seconds.".format(time.time() - start))

    start = time.time()
    rep = net.forward(alignedFace)
    if verbose:
        print("  + OpenFace forward pass took {} seconds.".format(time.time() - start))
        print("Representation:")
        print(rep)
        print("-----\n")
    return rep

@csrf_exempt
def cam_authorize(request):
    # global rtsp_url
    # align = openface.AlignDlib("/home/out/development/gentelella/app/static/openface/shape_predictor_68_face_landmarks.dat")
    # net = openface.TorchNeuralNet("/home/out/development/gentelella/app/static/openface/nn4.small2.v1.t7", 96)
    # bgrImg = cv2.imread("/home/out/development/gentelella/app/static/images/tony-1.png")
    # video = cv2.VideoCapture("/home/out/development/gentelella/app/static/images/test.MP4")
    # success, realImg = video.read()
    # source = getRep(align, net, bgrImg, 96)
    # if isinstance(source, str):
    #     print(source)
    #     if source == "Unable to load image":
    #         return HttpResponse(json.dumps({'status' : 'DETECT ERROR'}), content_type="application/json")
    #     if source == "Unable to find face":
    #         return HttpResponse(json.dumps({'status' : 'NO PERSON1'}), content_type="application/json")
    #     if source == "Unable to align":
    #         return HttpResponse(json.dumps({'status' : 'FIX ALIGN'}), content_type="application/json")
    # target = getRep(align, net, realImg, 96)
    # if isinstance(target, str):
    #     print(target)
    #     if target == "Unable to load image":
    #         return HttpResponse(json.dumps({'status' : 'DETECT ERROR'}), content_type="application/json")
    #     if target == "Unable to find face":
    #         return HttpResponse(json.dumps({'status' : 'NO PERSON2'}), content_type="application/json")
    #     if target == "Unable to align":
    #         return HttpResponse(json.dumps({'status' : 'FIX ALIGN'}), content_type="application/json")
    # d = source - target
    # np.set_printoptions(precision=2)
    # res_detect = np.dot(d, d)
    # print("====================")
    # print(res_detect)
    # print("====================")
    # if res_detect < 0.99:
    #     return HttpResponse(json.dumps({'status' : 'AUTHORIZED'}), content_type="application/json")
    # else :
    #     return HttpResponse(json.dumps({'status' : 'NOT AUTHORIZED'}), content_type="application/json")
    # return HttpResponse(json.dumps({'status' : 'NOT DETECTED'}), content_type="application/json")
    serial = request.GET.get("serial")
    print serial
    cam = Cameras.objects.filter(serial_number=serial)
    print cam[0].auth_state
    return HttpResponse(json.dumps({'status' : cam[0].auth_state}), content_type="application/json")

flag_auth = 0

def threaded_authorize(rtsp_url, serial):
    cam = Cameras.objects.filter(serial_number=serial)
    if cam[0].auth_state == "AUTHORIZED":
        return
    ### amazon
    ### /home/ubuntu/ipCameraAdmin/app/static/openface/shape_predictor_68_face_landmarks.dat
    align = openface.AlignDlib("/home/ubuntu/ipCameraAdmin/app/static/openface/shape_predictor_68_face_landmarks.dat")
    ### amazon
    ### /home/ubuntu/ipCameraAdmin/app/static/openface/nn4.small2.v1.t7
    net = openface.TorchNeuralNet("/home/ubuntu/ipCameraAdmin/app/static/openface/nn4.small2.v1.t7", 96)
    ### amazon
    ### /home/ubuntu/ipCameraAdmin/app/static/images/patroleum.jpg
    bgrImg = cv2.imread("/home/ubuntu/ipCameraAdmin/app/static/images/patroleum.jpg")
    ### amazon
    ### rtsp_url
    video = cv2.VideoCapture(rtsp_url)
    success, realImg = video.read()
    source = getRep(align, net, bgrImg, 96)
    if isinstance(source, str):
        print(source)
        if source == "Unable to load image":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="DETECT ERROR")
            return
        if source == "Unable to find face":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="NO PERSON1")
            return
        if source == "Unable to align":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="FIX ALIGN")
            return
    target = getRep(align, net, realImg, 96)
    if isinstance(target, str):
        print(target)
        if target == "Unable to load image":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="DETECT ERROR")
            return
        if target == "Unable to find face":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="NO PERSON2")
            return
        if target == "Unable to align":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="FIX ALIGN")
            return
    d = source - target
    np.set_printoptions(precision=2)
    res_detect = np.dot(d, d)
    print("====================")
    print(res_detect)
    print("====================")
    if res_detect < 0.99:
        if cam[0].auth_state != "AUTHORIZED":
            cam.update(auth_state="AUTHORIZED")
        return
    else :
        if cam[0].auth_state != "AUTHORIZED":
            cam.update(auth_state="NOT AUTHORIZED")
        return
    if cam[0].auth_state != "AUTHORIZED":
        cam.update(auth_state="NOT DETECTED")
    return HttpResponse(json.dumps({'status' : 'NOT DETECTED'}), content_type="application/json")

def threaded_main(rtsp_url, serial):
    print "thread is running"
    global flag_auth
    while flag_auth:
        cam = Cameras.objects.filter(serial_number=serial)
        if cam[0].auth_state == "AUTHORIZED":
            break
        thread = Thread(target = threaded_authorize, args = (rtsp_url, serial,))
        thread.start()
        time.sleep(1)

@csrf_exempt
def start_video(request):
    global flag_auth
    user = request.user.username
    rtsp_url = request.POST.get('streamUrl')
    high_url = request.POST.get('high')
    cam_url = request.POST.get('camurl')
    serial = request.POST.get('serial')

    #thread = Thread(target = threaded_main, args = (high_url, serial,))
    flag_auth = 1
    #thread.start()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def stop_record(request):
    global flag_auth
    flag_auth = 0
    serial = request.POST.get('serial')
    cam = Cameras.objects.filter(serial_number=serial)
    cam.update(auth_state="AUTHORIZING")
    print "flag_auth changed ========================="
    print flag_auth
    return HttpResponse(json.dumps({'status' : 'success', 'msg' : 'video stream stopped'}), content_type="application/json")

@csrf_exempt
def get_camera(request):
    serial = request.POST.get("serial")
    print(serial)
    object_list = Cameras.objects.filter(serial_number=serial)
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')