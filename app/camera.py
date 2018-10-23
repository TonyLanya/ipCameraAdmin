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
rtsp_url = ''

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
        global rtsp_url
        self.video = cv2.VideoCapture(rtsp_url)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        print("Now Loading")
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while video_status:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
@csrf_exempt
def video_feed(request):
    try:
        rtsp = request.POST.get('streamUrl')
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")

@csrf_exempt
def start_video(request):
    global rtsp_url
    global video_status
    rtsp_url = request.POST.get('streamUrl')
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