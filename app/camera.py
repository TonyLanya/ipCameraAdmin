from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse,StreamingHttpResponse, HttpResponseServerError
from django.core import serializers
from .models import Cameras, Emails, Users, Properties
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
from skimage import img_as_ubyte

### amazon
### /home/ubuntu/ipCameraAdmin/app/static
static_url = "/home/ubuntu/ipCameraAdmin/app/static"

### amazon
### /home/ubuntu/ipCameraAdmin/app/static/openface/shape_predictor_68_face_landmarks.dat
align = openface.AlignDlib(static_url + "/openface/shape_predictor_68_face_landmarks.dat")
### amazon
### /home/ubuntu/ipCameraAdmin/app/static/openface/nn4.small2.v1.t7
net = openface.TorchNeuralNet(static_url + "/openface/nn4.small2.v1.t7", 96)

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
    def __init__(self, rtsp_url, vtype):
        self.video = cv2.VideoCapture(rtsp_url)
        self.video_status = 1
        ### amazon
        ### /home/ubuntu/ipCameraAdmin/app/static/openface/lbpcascade_frontalface.xml
        self.vtype = vtype
        self.face_cascade = cv2.CascadeClassifier(static_url + '/openface/lbpcascade_frontalface.xml')
    def __del__(self):
        self.video.release()

    def detect_face(self, img):
        # convert the test image to gray image as opencv face detector expects gray images

        # let's detect multiscale (some images may be closer to camera than others) images
        # result is a list of faces


        img = np.uint8(img)
        faces = self.face_cascade.detectMultiScale(img,scaleFactor=1.45 ,minNeighbors=0)
        # if no faces are detected then return original img
        if (len(faces) == 0):
            return 0, None, None

        # under the assumption that there will be only one face,
        # extract the face area
        (x, y, w, h) = faces[0]

        # return only the face part of the image
        return 1, img[y:y + w, x:x + h], faces[0]

    def draw_rectangle(self, img, rect):
        (x, y, w, h) = rect
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255,0), 2)
        return img


    def get_frame(self):
        if (self.video.isOpened() == False):
            self.video_status = 0
            return None
        ret, image = self.video.read()
        if ret == False:
            self.video_status = 0
            return None
        flag, face, rect = self.detect_face(image)
        if flag:
            self.draw_rectangle(image, rect)
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
        vtype = request.GET.get('vtype')
        ### amazon
        ### rtsp
        return StreamingHttpResponse(gen(VideoCamera(rtsp)),content_type="multipart/x-mixed-replace;boundary=frame")
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
    serial = request.GET.get("serial")
    cam = Cameras.objects.filter(serial_number=serial)
    print cam[0].auth_state
    auth_res = cam[0].auth_res
    if auth_res != None:
        user = Users.objects.filter(pk=auth_res)
        prop_id = user[0].property_id
        prop = Properties.objects.filter(pk=prop_id)
        return HttpResponse(json.dumps({'status' : cam[0].auth_state, 'name' : user[0].name, 'phoneno' : user[0].phoneno, 'address' : prop[0].address, 'policeph' : prop[0].police}), content_type="application/json")
    return HttpResponse(json.dumps({'status' : cam[0].auth_state}), content_type="application/json")

flag_auth = 0

def threaded_authorize(rtsp_url, serial, sources, users):
    print serial
    cam = Cameras.objects.filter(serial_number=serial)
    if cam[0].auth_state == "AUTHORIZED":
        return 1
    ### amazon
    ### video = cv2.VideoCapture(rtsp_url)
    video = cv2.VideoCapture(rtsp_url)
    success, realImg = video.read()
    target = getRep(align, net, realImg, 96)
    if isinstance(target, str):
        print(target)
        if target == "Unable to load image":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="DETECT ERROR")
            return 0
        if target == "Unable to find face":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="NO PERSON2")
            return 0
        if target == "Unable to align":
            if cam[0].auth_state != "AUTHORIZED":
                cam.update(auth_state="FIX ALIGN")
            return 0
    flag = 0
    inf = 0
    for source in sources:
        d = source - target
        np.set_printoptions(precision=2)
        res_detect = np.dot(d, d)
        print("====================")
        print(res_detect)
        print("====================")
        if res_detect < 0.99:
            flag = 1
            break
        else:
            inf = inf + 1
    if flag:
        if cam[0].auth_state != "AUTHORIZED":
            cam.update(auth_state="AUTHORIZED")
            cam.update(auth_res=users[inf])
        return 1
    else :
        if cam[0].auth_state != "AUTHORIZED":
            cam.update(auth_state="NOT AUTHORIZED")
        return 0
    if cam[0].auth_state != "AUTHORIZED":
        cam.update(auth_state="NOT DETECTED")
    return 0

def get_source(sourceurl):
    #cam = Cameras.objects.filter(serial_number=serial)
    bgrImg = cv2.imread(sourceurl)
    source = getRep(align, net, bgrImg, 96)
    if isinstance(source, str):
        # print(source)
        if source == "Unable to load image":
            # if cam[0].auth_state != "AUTHORIZED":
            #     cam.update(auth_state="DETECT ERROR")
            return 0, None
        if source == "Unable to find face":
            # if cam[0].auth_state != "AUTHORIZED":
            #     cam.update(auth_state="NO PERSON1")
            return 0, None
        if source == "Unable to align":
            # if cam[0].auth_state != "AUTHORIZED":
            #     cam.update(auth_state="FIX ALIGN")
            return 0, None
    return 1, source

def threaded_main(rtsp_url, serial):
    print "thread is running"
    ### amazon
    ### /home/ubuntu/ipCameraAdmin/app/static/images/patroleum.jpg
    cam = Cameras.objects.filter(serial_number=serial)
    prop_id = cam[0].property_id
    users = Users.objects.filter(property_id=prop_id)
    #sourceurl = "/home/out/development/gentelella/app/static/images/" + prop_id + "/" + user[1].name + ".png"
    #print "============="
    #print sourceurl
    #print "============="
    #source = get_source(sourceurl, serial)
    #np.savetxt("/home/out/development/gentelella/app/static/images/" + prop_id + "/" + user[1].name + ".csv", source, delimiter=",")
    print "/////////////////"
    print len(users)
    print "/////////////////"
    sources = []
    usrs = []
    for user in users:
        if user.registered:
            sourceurl = static_url + "/images/" + prop_id + "/" + user.name + ".csv"
            source = np.genfromtxt(sourceurl, delimiter=',')
            sources.append(source)
            usrs.append(user.id)
    print sources
    if len(sources) == 0:
        return
    while 1:
        cam = Cameras.objects.filter(serial_number=serial)
        print cam[0].auth_user
        if cam[0].auth_user == None:
            break
        if cam[0].auth_state == "AUTHORIZED":
            break
        #thread = Thread(target = threaded_authorize, args = (rtsp_url, serial,))
        if threaded_authorize(rtsp_url, serial, sources, usrs):
            break
        #thread.start()
        #time.sleep(1)


@csrf_exempt
def start_video(request):
    global flag_auth
    user = request.user.username
    rtsp_url = request.POST.get('streamUrl')
    high_url = request.POST.get('high')
    cam_url = request.POST.get('camurl')
    serial = request.POST.get('serial')
    Cameras.objects.filter(serial_number=serial).update(auth_state="AUTHORIZING")
    Cameras.objects.filter(serial_number=serial).update(auth_res=None)

    thread = Thread(target = threaded_main, args = (high_url, serial,))
    flag_auth = 1
    #threaded_authorize(high_url, serial)
    thread.start()
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def stop_record(request):
    global flag_auth
    flag_auth = 0
    serial = request.POST.get('serial')
    cam = Cameras.objects.filter(serial_number=serial)
    cam.update(auth_state="AUTHORIZING")
    cam.update(auth_user=None)
    cam.update(auth_res=None)
    return HttpResponse(json.dumps({'status' : 'success', 'msg' : 'video stream stopped'}), content_type="application/json")

@csrf_exempt
def get_camera(request):
    serial = request.POST.get("serial")
    object_list = Cameras.objects.filter(serial_number=serial)
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')

@csrf_exempt
def get_cam(request):
    # try:
    id = request.POST.get("id")
    cam = Cameras.objects.filter(pk=id)
    res = serializers.serialize('json', cam)
    return HttpResponse(res, content_type='application/json')
    # except:
    #     return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def remove_cam(request):
    try:
        serial = request.POST.get("serial")
        camera = Cameras.objects.filter(serial_number=serial)
        camera.delete()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def update_cam(request):
    try:
        id = request.POST.get("id")
        cam = Cameras.objects.get(pk=id)
        cam.name = request.POST.get("name")
        cam.address = request.POST.get("address")
        cam.port = request.POST.get("port")
        cam.login = request.POST.get("login")
        cam.password = request.POST.get("password")
        cam.serial_number = request.POST.get("serial")
        cam.property_id = request.POST.get("prop")
        cam.save()
        return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({'status' : "failed"}), content_type="application/json")

@csrf_exempt
def view_cam(request):
    try:
        id = request.POST.get("id")
        cam = Cameras.objects.filter(pk=id)
        res = serializers.serialize('json', cam)
        return HttpResponse(res, content_type="application/json")
    except:
        return HttpResponse('')
