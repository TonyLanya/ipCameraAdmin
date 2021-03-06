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
#import openface
import numpy as np
from threading import Thread
#from skimage import img_as_ubyte
import pickle
import imutils

### amazon
### /home/ubuntu/ipCameraAdmin/app/static
static_url = "/root/ipCameraAdmin/app/static"

### amazon
### /home/ubuntu/ipCameraAdmin/app/static/openface/shape_predictor_68_face_landmarks.dat
#align = openface.AlignDlib(static_url + "/openface/shape_predictor_68_face_landmarks.dat")
### amazon
### /home/ubuntu/ipCameraAdmin/app/static/openface/nn4.small2.v1.t7
#net = openface.TorchNeuralNet(static_url + "/openface/nn4.small2.v1.t7", 96)

protoPath = static_url + "/face_detection_model/deploy.prototxt"
modelPath = static_url + "/face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

embedder = cv2.dnn.readNetFromTorch(static_url + "/openface_nn4.small2.v1.t7")

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
    def __init__(self, rtsp_url, vtype, recognizer, le):
        self.video = cv2.VideoCapture(rtsp_url)
        self.video_status = 1
        ### amazon
        ### /home/ubuntu/ipCameraAdmin/app/static/openface/lbpcascade_frontalface.xml
        self.vtype = vtype
        self.recognizer = recognizer
        self.le = le
        self.face_cascade = cv2.CascadeClassifier(static_url + '/openface/lbpcascade_frontalface.xml')
    def __del__(self):
        self.video.release()

    def detect_face(self, frame):
        frame = imutils.resize(frame, width=600)
        (h, w) = frame.shape[:2]

        # construct a blob from the image
        imageBlob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

        # apply OpenCV's deep learning-based face detector to localize
        # faces in the input image
        detector.setInput(imageBlob)
        detections = detector.forward()

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections
            if confidence > 0.5:
                print("YOU+++++")
                # compute the (x, y)-coordinates of the bounding box for
                # the face
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # extract the face ROI
                face = frame[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]

                # ensure the face width and height are sufficiently large
                if fW < 20 or fH < 20:
                    continue

                # construct a blob for the face ROI, then pass the blob
                # through our face embedding model to obtain the 128-d
                # quantification of the face
                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                    (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward()

                # perform classification to recognize the face
                preds = self.recognizer.predict_proba(vec)[0]
                j = np.argmax(preds)
                proba = preds[j]
                name = self.le.classes_[j]
                # draw the bounding box of the face along with the
                # associated probability
                text = "{}: {:.2f}%".format(name, proba * 100)
                y = startY - 10 if startY - 10 > 10 else startY + 10
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    (0, 0, 255), 2)
                #cv2.putText(frame, text, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        return frame

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
        try:
            print("try----")
            image = self.detect_face(image)
            print("YYYYYYYY")
        except:
            print("NNNNNNNNNNN")
            k=1
        # if flag:
        #     self.draw_rectangle(image, rect)
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
            #time.sleep(5)

@gzip.gzip_page
@csrf_exempt
def video_feed(request):
    try:
        rtsp = request.GET.get('streamUrl')
        vtype = request.GET.get('vtype')
        cam = Cameras.objects.filter(serial_number=request.GET.get('serial'))
        prop_id = cam[0].property_id
        with open(static_url + "/face_models/" + prop_id + "/recognizer.pickle", 'rb') as f:
            recognizer = pickle.load(f)
        with open(static_url + "/face_models/" + prop_id + "/le.pickle", 'rb') as l:
            le = pickle.load(l)
        rtsp = rtsp + '&subtype=1'
        ### amazon
        ### rtsp
        return StreamingHttpResponse(gen(VideoCamera(rtsp, vtype, recognizer, le)),content_type="multipart/x-mixed-replace;boundary=frame")
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
    print(cam[0].auth_state)
    print(cam[0].auth_res)
    auth_res = cam[0].auth_res
    if auth_res != None:
        user = Users.objects.filter(trained_name=auth_res)
        prop_id = user[0].property_id
        prop = Properties.objects.filter(pk=prop_id)
        return HttpResponse(json.dumps({'status' : cam[0].auth_state, 'name' : user[0].name, 'phoneno' : user[0].phoneno, 'address' : prop[0].address, 'policeph' : prop[0].police}), content_type="application/json")
    return HttpResponse(json.dumps({'status' : cam[0].auth_state}), content_type="application/json")

flag_auth = 0

def threaded_authorize(video, serial, recognizer, le):
    print(serial)
    cam = Cameras.objects.filter(serial_number=serial)
    if cam[0].auth_state == "AUTHORIZED":
        return 1
    ### amazon
    ### video = cv2.VideoCapture(rtsp_url)
    #video = cv2.VideoCapture(static_url + "/images/test.MP4")



    ret, frame = video.read()
    frame = imutils.resize(frame, width=600)
    (h, w) = frame.shape[:2]

    # construct a blob from the image
    imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(frame, (300, 300)), 1.0, (300, 300),
		(104.0, 177.0, 123.0), swapRB=False, crop=False)

    # apply OpenCV's deep learning-based face detector to localize
	# faces in the input image
    detector.setInput(imageBlob)
    detections = detector.forward()

    # loop over the detections
    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > 0.5:
            # compute the (x, y)-coordinates of the bounding box for
            # the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the face ROI
            face = frame[startY:endY, startX:endX]
            (fH, fW) = face.shape[:2]

            # ensure the face width and height are sufficiently large
            if fW < 20 or fH < 20:
                continue

            # construct a blob for the face ROI, then pass the blob
            # through our face embedding model to obtain the 128-d
            # quantification of the face
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                (96, 96), (0, 0, 0), swapRB=True, crop=False)
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            # perform classification to recognize the face
            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            if name != "unknown":
                if cam[0].auth_state != "AUTHORIZED":
                    cam.update(auth_state="AUTHORIZED")
                    cam.update(auth_res=name)
                return 1
            else:
                if cam[0].auth_state != "AUTHORIZED":
                    if cam[0].auth_state != "NOT AUTHORIZED":
                        cam.update(auth_state="NOT AUTHORIZED")
                return 0

            # draw the bounding box of the face along with the
            # associated probability
            # text = "{}: {:.2f}%".format(name, proba * 100)
            # y = startY - 10 if startY - 10 > 10 else startY + 10
            # cv2.rectangle(frame, (startX, startY), (endX, endY),
            # 	(0, 0, 255), 2)
            # cv2.putText(frame, text, (startX, y),
            # 	cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

    if cam[0].auth_state != "AUTHORIZED":
        if cam[0].auth_state != "NOT DETECTED":
            cam.update(auth_state="NOT DETECTED")



    # success, realImg = video.read()
    # target = getRep(align, net, realImg, 96)
    # if isinstance(target, str):
    #     print(target)
    #     if target == "Unable to load image":
    #         if cam[0].auth_state != "AUTHORIZED":
    #             cam.update(auth_state="DETECT ERROR")
    #         return 0
    #     if target == "Unable to find face":
    #         if cam[0].auth_state != "AUTHORIZED":
    #             cam.update(auth_state="NO PERSON2")
    #         return 0
    #     if target == "Unable to align":
    #         if cam[0].auth_state != "AUTHORIZED":
    #             cam.update(auth_state="FIX ALIGN")
    #         return 0
    # flag = 0
    # inf = 0
    # for source in sources:
    #     d = source - target
    #     np.set_printoptions(precision=2)
    #     res_detect = np.dot(d, d)
    #     print("====================")
    #     print(res_detect)
    #     print("====================")
    #     if res_detect < 0.99:
    #         flag = 1
    #         break
    #     else:
    #         inf = inf + 1
    # if flag:
    #     if cam[0].auth_state != "AUTHORIZED":
    #         cam.update(auth_state="AUTHORIZED")
    #         cam.update(auth_res=users[inf])
    #     return 1
    # else :
    #     if cam[0].auth_state != "AUTHORIZED":
    #         cam.update(auth_state="NOT AUTHORIZED")
    #     return 0
    # if cam[0].auth_state != "AUTHORIZED":
    #     cam.update(auth_state="NOT DETECTED")
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
    print("thread is running")
    # cam = Cameras.objects.filter(serial_number=serial)
    # prop_id = cam[0].property_id
    # users = Users.objects.filter(property_id=prop_id)
    # sources = []
    # usrs = []
    # for user in users:
    #     if user.registered:
    #         sourceurl = static_url + "/images/" + prop_id + "/" + user.name + ".csv"
    #         source = np.genfromtxt(sourceurl, delimiter=',')
    #         sources.append(source)
    #         usrs.append(user.id)
    # print sources
    # if len(sources) == 0:
    #     return
    cam = Cameras.objects.filter(serial_number=serial)
    prop_id = cam[0].property_id
    with open(static_url + "/face_models/" + prop_id + "/recognizer.pickle", 'rb') as f:
        recognizer = pickle.load(f)
    with open(static_url + "/face_models/" + prop_id + "/le.pickle", 'rb') as l:
        le = pickle.load(l)
    #video = cv2.VideoCapture(rtsp_url)
    video = cv2.VideoCapture(rtsp_url)
    while 1:
        cam = Cameras.objects.filter(serial_number=serial)
        print(cam[0].auth_user)
        if cam[0].auth_user == None:
            break
        if cam[0].auth_state == "AUTHORIZED":
            break
        #thread = Thread(target = threaded_authorize, args = (rtsp_url, serial,))
        try:
            if threaded_authorize(video, serial, recognizer, le):
                break
        except:
            k=1
        #thread.start()
        #time.sleep(1)


@csrf_exempt
def start_video(request):
    global flag_auth
    user = request.user.username
    rtsp_url = request.POST.get('streamUrl')
    high_url = request.POST.get('high')
    print("++++++++++++++++++++++++")
    print(high_url)
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
def reset_cam(request):
    id = request.POST.get("id")
    cam = Cameras.objects.filter(pk=id)
    cam.update(auth_user=None)
    return HttpResponse(json.dumps({'status' : "success"}), content_type="application/json")

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
