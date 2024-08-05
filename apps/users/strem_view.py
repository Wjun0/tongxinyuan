import datetime
import re
import os
import mimetypes
from wsgiref.util import FileWrapper
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render
from apps.users.models import Media, Document, User
from libs import ajax
import requests

from utils.generate_jwt import jwt_decode


def get_url_response(url):
    try:
        resp = requests.get(url, verify=False)
        return resp
    except Exception as e:
        return f"{url}  链接不能访问！"


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def stream_video(request, file_id):
    f = Media.objects.filter(file_id=file_id).first()
    if not f:
        # return HttpResponse('页面不存在', status=404)
        return render(request, 'error.html', context={"message": "页面不存在"})
    if f.time_limite == 1 or f.time_limite == "1":
        now = timezone.now()
        if f.start_time > now:
            return render(request, 'error.html', context={"message": "页面未生效"})
        if not f.start_time <  now < f.end_time:
            # return HttpResponse('页面已失效', status=400)
            return render(request, 'error.html', context={"message": "页面已失效"})
    ##########
    # url 类型的requests 请求访问
    if f.type == "url":
        # return HttpResponse(get_url_response(f.original_url))
        return HttpResponseRedirect(f.original_url)
    ############

    filename = f"media/qrcode/{f.path}"
    video_path = os.path.join(settings.BASE_DIR, filename)

    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    size = os.path.getsize(video_path)
    content_type, encoding = mimetypes.guess_type(video_path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 2  # 2M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(video_path, offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        resp = StreamingHttpResponse(FileWrapper(open(video_path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
        # url = settings.DOMAIN + "/user/download/" + file_id + "/"
        # return ajax.ajax_template(request, 'download_media.html', {'url': url})
        # return ajax.ajax_template(request, '1.html', {'url': url})
    resp['Accept-Ranges'] = 'bytes'
    return resp



def verify(token):
    try:
        data = jwt_decode(token)
        user_id = data.get("data", {}).get('user_id')
        obj = User.objects.filter(user_id=user_id, token=token, role__lte=3).first()
        now = timezone.now()
        if obj.token_exp + datetime.timedelta(hours=24) > now:
            if obj.status == "used":
                return True
    except Exception as e:
        return False

def PCstream_video(request, file_id):
    # token = request.META.get('HTTP_AUTHORIZATION')
    # if not verify(token):
    #     return render(request, 'error.html', context={"message": "认证信息未提供！"})
    # f = Media.objects.filter(file_id=file_id).first()
    # if not f:
    #     # return HttpResponse('页面不存在', status=404)
    #     return render(request, 'error.html', context={"message": "页面不存在"})
    # if f.type == "url":
    #     # return HttpResponse(get_url_response(f.original_url))
    #     return HttpResponseRedirect(f.original_url)
    f = Document.objects.filter(docfile=file_id).first()
    if not f:
        return HttpResponse('页面不存在', status=404)
    ############
    filename = f"media/qrcode/{f.filename}"
    video_path = os.path.join(settings.BASE_DIR, filename)
    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    size = os.path.getsize(video_path)
    content_type, encoding = mimetypes.guess_type(video_path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 2  # 2M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(video_path, offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        resp = StreamingHttpResponse(FileWrapper(open(video_path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
        # url = settings.DOMAIN + "/user/download/" + file_id + "/"
        # return ajax.ajax_template(request, 'download_media.html', {'url': url})
        # return ajax.ajax_template(request, '1.html', {'url': url})
    resp['Accept-Ranges'] = 'bytes'
    return resp

def play_media(request, file_id):
    f = Media.objects.filter(file_id=file_id).first()
    if not f:
        # return HttpResponse('页面不存在', status=404)
        return render(request, 'error.html', context={"message": "页面不存在"})
    if f.time_limite == 1 or f.time_limite == "1":
        now = timezone.now()
        if f.start_time > now:
            return render(request, 'error.html', context={"message": "页面未生效"})
        if not f.start_time < now < f.end_time:
            # return HttpResponse('页面已失效', status=400)
            return render(request, 'error.html', context={"message": "页面已失效"})
    ##########
    # url 类型的requests 请求访问
    if f.type == "url":
        # return HttpResponse(get_url_response(f.original_url))
        return HttpResponseRedirect(f.original_url)
    ############
    f_type = f.path.split('.')[-1]
    url = settings.DOMAIN + "/user/play/" + file_id + "/"
    type = f"video/{f_type}"
    return render(request, 'play_media.html', context={"url": url, "type": type})
