from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from weixin import WXAPPAPI
import jwt
import datetime, base64, time, re
from utils.generate_jwt import generate_jwt
from .models import User
from .serializers import UserSerizlizers


class LoginAPIView(CreateAPIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        api = WXAPPAPI(appid=settings.WX_APPID, app_secret=settings.WX_SECRET)
        info = api.exchange_code_for_session_key(code=code)
        print(info)
        session_key = info.get('session_key')
        openid = info.get('openid')
        user_id = base64.b64encode(openid.encode()).decode()
        user_info = {"user_id": user_id,
                     "iat": time.time()}
        access_token = generate_jwt(user_info, 1)
        refresh_token = generate_jwt(user_info, 24)
        return Response({"access_token": access_token, "refresh_token": refresh_token})


class RegisterAPIView(CreateAPIView):
    # 登录注册接口
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        pwd = data.get('password', '')
        mobile = data.get('mobile', '')
        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(name):
            return Response({"message": "用户名支持文本与字母数字，不超过20字符"}, status=400)
        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(pwd):
            return Response({"message": "密码支持文本与字母数字，不超过20字符"}, status=400)
        if not re.compile(r'(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$').search(mobile):
            return Response({"message": "电话号码格式不正确！"}, status=400)
        if len(name) > 20:
            return Response({"message": "用户名长度超过20个字符！"}, status=400)
        if len(pwd) > 20:
            return Response({"message": "密码长度超过20个字符！"}, status=400)
        obj = self.get_queryset().filter(name=name).first()
        if obj:  # 登录逻辑
            if obj.status != "used":  # 用户状态不是启用的
                return Response({"message": "用户名已被占用"}, status=400)
            if obj.password == pwd:
                data = {"user_id": obj.id, "iat": time.time()}
                access_token = generate_jwt(data, 1)
                obj.token = access_token
                obj.exp_time = datetime.datetime.now()
                obj.save()
                Response({"message": "ok", "access_token": access_token})
                # refresh_token = generate_jwt(data, 24)
                # return Response({"access_token": access_token, "refresh_token": refresh_token})
            return Response({"message": "用户名与密码不符"}, status=400)
        else:  # 注册逻辑
            # 权限列表申请中
            cre = self.get_queryset().create(name=name, password=pwd, mobile=mobile, status="waiting")
            return Response({"message": "注册成功，请等待管理员审核"})


class UserAuditAPIView(ListAPIView, CreateAPIView, UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerizlizers

    def create(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id', '')
        name = data.get('name', '')
        role = data.get('role', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        obj = get_object_or_404(self.get_queryset(), id=id, name=name)
        obj.role = role
        obj.start_time = start_time
        obj.end_time = end_time
        obj.save()
        return Response({"message": "success"})

    def put(self, request, *args, **kwargs):
        data = request.data
        id = data.get('id', '')
        name = data.get('name', '')
        status = data.get('status', '')
        if status not in ['used', 'waiting', 'deleted']:
            return Response({"message": "bad request"}, status=400)
        obj = get_object_or_404(self.get_queryset(), id=id, name=name)
        obj.status = status
        obj.save()
        return Response({"message": "success"})


