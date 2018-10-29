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
#from PIL import Image
import io
import openface
import numpy as np
#import boto3
rtsp_url = ''
BUCKET = "iocameraadmin.skydeveloperonline.com"
KEY_SOURCE = "patroleum/patroleum.jpg"

tt = 112
shard = True
data = None
video_status = False

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

@csrf_exempt
def view_camera(request):
    return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'There is no endpoint'}), content_type="application/json")
    # STREAM_NAME = request.POST.get('streamName')
    # kvs = boto3.client("kinesisvideo")
    # # Grab the endpoint from GetDataEndpoint
    # endpoint = kvs.get_data_endpoint(
    #     APIName="GET_HLS_STREAMING_SESSION_URL",
    #     StreamName=STREAM_NAME
    # )
    # print(endpoint)
    # try:
    #     kvs = boto3.client("kinesisvideo")
    #     # Grab the endpoint from GetDataEndpoint
    #     endpoint = kvs.get_data_endpoint(
    #         APIName="GET_HLS_STREAMING_SESSION_URL",
    #         StreamName=STREAM_NAME
    #     )
    #     print(endpoint)
    #     # Grab the HLS Stream URL from the endpoint
    #     if ( 'DataEndpoint' in endpoint ):
    #         kvam = boto3.client("kinesis-video-archived-media", endpoint_url=endpoint['DataEndpoint'])
    #         print("------kvam---------")
    #         print(kvam)
    #         url = kvam.get_hls_streaming_session_url(
    #             StreamName=STREAM_NAME,
    #             PlaybackMode="LIVE"
    #         )
    #         print("------url-----")
    #         print(url)
    #         if ( 'HLSStreamingSessionURL' in url ):
    #             context = { "url" : url['HLSStreamingSessionURL'] }
    #             return HttpResponse(json.dumps({'status' : 'success', 'stream' : STREAM_NAME, 'url' : url['HLSStreamingSessionURL']}), content_type="application/json")
    #         else:
    #             context = {"url" : None}
    #             return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'Cant fetch HLSStreamingSessionURL', 'stream' : STREAM_NAME}), content_type="application/json")
    #     else:
    #         context = {"url" : None}
    #         return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'There is no endpoint', 'stream' : STREAM_NAME}), content_type="application/json")
    # except:
    #     context =  {"url" : None}
    #     return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'exception : cannot view camera', 'stream' : STREAM_NAME}), content_type="application/json")

@csrf_exempt
def start_record(request):
    return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'There is no endpoint'}), content_type="application/json")
    # global tt
    # global shard
    # STREAM_NAME = request.POST.get('streamName')
    # shardId="shardId-000000000000"
    # limit=1

    # client=boto3.client('kinesis')
    # response = client.get_shard_iterator(
    #     StreamName=STREAM_NAME,
    #     ShardId=shardId,
    #     ShardIteratorType='TRIM_HORIZON'
    # )
    # print("ShardIterator : ", response["ShardIterator"])
    # shardIterator=response["ShardIterator"]
    # response = client.get_records(
    #     ShardIterator=shardIterator,
    #     Limit=limit
    # )
    # shard = True
    # while shard:
    #     tt = tt + 1
    #     print("+++++++SHARD+++++++")
    #     print(shard)
    #     today = datetime.datetime.now()
    #     print("-------" + today.strftime("%Y-%m-%d %H:%M:%S") + "-------")

    #     print("Records")
    #     records = response["Records"]
    #     if( len(records) > 0):
    #         data = records[0]["Data"].decode("utf-8")
    #     if "NextShardIterator" in response:
    #         response = client.get_records(
    #             ShardIterator=response["NextShardIterator"],
    #             Limit=limit
    #         )
    #     else:
    #         shard = False

class VideoCamera(object):
    def __init__(self):
        #self.video = cv2.VideoCapture("D:\\1work\\36-django-ipcamera\\django-gentelella\\ipCameraAdmin\\app\\vidme.mp4")
        self.video = cv2.VideoCapture("/home/out/development/gentelella/app/static/images/test.MP4")
    def __del__(self):
        self.video.release()

    def get_frame(self):
        print(self.video.isOpened())
        if (self.video.isOpened() == False):
            return None
        ret,image = self.video.read()
        print("Now Loading")
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while video_status:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        #time.sleep(1)

@gzip.gzip_page
@csrf_exempt
def video_feed(request):
    print("video_feed")
    try:
        rtsp = request.POST.get('streamUrl')
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")


#### OPENFCACE FUNCTION
def getRep(align, net, bgrImg, imgDim, verbose = None):
    #if args.verbose:
    #    print("Processing {}.".format(imgPath))
    #bgrImg = cv2.imread(imgPath)
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
    ############# AMAZON
    # global rtsp_url
    # video = cv2.VideoCapture(0)
    # #video = cv2.VideoCapture("D:\\1work\\36-django-ipcamera\\django-gentelella\\ipCameraAdmin\\app\\vidme.mp4")
    # success, frame = video.read()
    # if success == False:
    #     return HttpResponse(json.dumps({'status' : 'AUTHORIZING'}), content_type="application/json")
    # pil_img = Image.fromarray(frame) # convert opencv frame (with type()==numpy) into PIL Image
    # stream = io.BytesIO()
    # pil_img.save(stream, format='JPEG') # convert PIL Image to Bytes
    # bin_img = stream.getvalue()
    # flag_auth = 0


    # threshold = 80
    # rekognition = boto3.client("rekognition")
    # try:
    #     response = rekognition.compare_faces(
    #         SourceImage={
    #             "S3Object": {
    #                 "Bucket": BUCKET,
    #                 "Name": KEY_SOURCE,
    #                 }
    #         },
    #         TargetImage={
    #             'Bytes': bin_img
    #         },
    #         SimilarityThreshold=80,
    #     )
    # except:
    #     return HttpResponse(json.dumps({'status' : 'NO ONE DETECTED'}), content_type="application/json")
    # matches =  response['FaceMatches']
    # if ( len(matches) ):
    #     for match in matches:
    #         print("Target Face ({Confidence}%)".format(**match['Face']))
    #         print("  Similarity : {}%".format(match['Similarity']))
    #         if match['Similarity'] > 80 :
    #             flag_auth = 1
    #     if flag_auth == 1 :
    #         return HttpResponse(json.dumps({'status' : 'AUTHORIZED'}), content_type="application/json")
    #     else :
    #         return HttpResponse(json.dumps({'status' : 'NOT AUTHORIZED'}), content_type="application/json")
    # return HttpResponse(json.dumps({'status' : 'NO ONE DETECTED'}), content_type="application/json")
    
    ################ openface
    global rtsp_url
    align = openface.AlignDlib("/home/out/development/gentelella/app/static/openface/shape_predictor_68_face_landmarks.dat")
    net = openface.TorchNeuralNet("/home/out/development/gentelella/app/static/openface/nn4.small2.v1.t7", 96)
    bgrImg = cv2.imread("/home/out/development/gentelella/app/static/images/tony-1.png")
    video = cv2.VideoCapture("/home/out/development/gentelella/app/static/images/test.MP4")
    success, realImg = video.read()
    source = getRep(align, net, bgrImg, 96)
    if isinstance(source, str):
        print(source)
        if source == "Unable to load image":
            return HttpResponse(json.dumps({'status' : 'DETECT ERROR'}), content_type="application/json")
        if source == "Unable to find face":
            return HttpResponse(json.dumps({'status' : 'NO PERSON1'}), content_type="application/json")
        if source == "Unable to align":
            return HttpResponse(json.dumps({'status' : 'FIX ALIGN'}), content_type="application/json")
    target = getRep(align, net, realImg, 96)
    if isinstance(target, str):
        print(target)
        if target == "Unable to load image":
            return HttpResponse(json.dumps({'status' : 'DETECT ERROR'}), content_type="application/json")
        if target == "Unable to find face":
            return HttpResponse(json.dumps({'status' : 'NO PERSON2'}), content_type="application/json")
        if target == "Unable to align":
            return HttpResponse(json.dumps({'status' : 'FIX ALIGN'}), content_type="application/json")
    d = source - target
    np.set_printoptions(precision=2)
    res_detect = np.dot(d, d)
    print("====================")
    print(res_detect)
    print("====================")
    if res_detect < 0.99:
        return HttpResponse(json.dumps({'status' : 'AUTHORIZED'}), content_type="application/json")
    else :
        return HttpResponse(json.dumps({'status' : 'NOT AUTHORIZED'}), content_type="application/json")
    return HttpResponse(json.dumps({'status' : 'NOT DETECTED'}), content_type="application/json")


@csrf_exempt
def start_video(request):
    global rtsp_url
    global video_status
    rtsp_url = request.POST.get('streamUrl')
    cam_url = request.POST.get('camurl')

    video_status = True
    return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def stop_record(request):
    global rtsp_url
    global video_status
    rtsp_url = ''
    video_status = False
    return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'There is no endpoint'}), content_type="application/json")
    # global shard
    # shard = False
    # print("&&&&&&&&&& changed shard &&&&&&&&&&")
    # print(shard)
    # return HttpResponse(json.dumps({'status' : 'success'}), content_type="application/json")

@csrf_exempt
def get_record(request):
    return HttpResponse(json.dumps({'status' : 'failed', 'msg' : 'There is no endpoint'}), content_type="application/json")
    # global data
    # if( data != None) :
    #     record = json.loads(data)
    #     return HttpResponse(json.dumps({'status' : 'success', 'record' : record}), content_type="application/json")
    # else:
    #     return HttpResponse(json.dumps({'status' : 'success', 'record' : data}), content_type="application/json")

@csrf_exempt
def get_camera(request):
    serial = request.POST.get("serial")
    print(serial)
    object_list = Cameras.objects.filter(serial_number=serial)
    json = serializers.serialize('json', object_list)
    return HttpResponse(json, content_type='application/json')