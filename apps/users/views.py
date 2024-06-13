from django.conf import settings
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER, FORMAT_DATETIME
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from weixin import WXAPPAPI
import jwt
import datetime, base64, time, re
from utils.generate_jwt import generate_jwt
from .models import User
from drf_yasg.utils import swagger_auto_schema

from .permission import LoginPermission
from .serializers import UserSerizlizers
import uuid


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerizlizers
    @swagger_auto_schema(
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'name': Schema(type=TYPE_STRING),
                'password': Schema(type=TYPE_STRING),
                'mobile': Schema(type=TYPE_STRING)
            },
        ),
        # responses={200: Schema(type=TYPE_STRING)},
        operation_summary="后台注册接口",
        operation_description=""
    )
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
        obj = self.get_queryset().filter(Q(name=name) | Q(mobile=mobile)).first()
        if obj:
            return Response({"message": "用户名或手机号已注册！", "code": "400"})
        user_id = "PC_" + str(uuid.uuid4())
        cre = self.get_queryset().create(user_id=user_id, name=name, password=pwd, mobile=mobile, status="waiting")
        return Response({"message": "注册成功，请等待管理员审核", "code": 200})


class LoginAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerizlizers

    @swagger_auto_schema(
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'name': Schema(type=TYPE_STRING),
                'password': Schema(type=TYPE_STRING)
            },
        ),
        # responses={200: Schema(type=TYPE_STRING)},
        operation_summary="后台登录接口",
        operation_description=""
    )
    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        pwd = data.get('password', '')
        obj = self.get_queryset().filter(Q(name=name) | Q(mobile=name)).first()
        if not obj:
            return Response({"message": "用户名不存在！", "code": 400})
        if obj.status != "used":  # 用户状态不是启用的
            return Response({"message": "该用户未启用！", "code": 400})
        if obj.password == pwd:
            data = {"user_id": obj.user_id, "iat": time.time()}
            access_token = generate_jwt(data, 1)
            refresh_token = generate_jwt(data, 24)
            obj.token = access_token
            obj.exp_time = datetime.datetime.now()
            obj.save()
            return Response({"message": "ok", "code": 200, "data": {"access_token": access_token, "refresh_token": refresh_token}})
        else:
            return Response({"message": "用户名或密码错误！", "code": 400})


class UserAuditAPIView(ListAPIView, CreateAPIView, UpdateAPIView):
    queryset = User.objects.filter(~Q(role=100))
    serializer_class = UserSerizlizers
    permission_classes = (LoginPermission, )

    @swagger_auto_schema(
        operation_summary="获取用户列表",
        operation_description=""
    )
    def get(self, request, *args, **kwargs):
        """
        获取用户列表
        """
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="审核用户，赋予权限",
        operation_description="",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'id': Schema(type=TYPE_INTEGER),
                'name': Schema(type=TYPE_STRING),
                'role': Schema(type=TYPE_INTEGER),
                'start_time': Schema(type=FORMAT_DATETIME),
                'end_time': Schema(type=FORMAT_DATETIME),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        """
        审核用户，赋予权限
        """
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

    @swagger_auto_schema(operation_summary="注销|启用 用户")
    def put(self, request, *args, **kwargs):
        """
        注销|启用 用户
        """
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


class UserLoginAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerizlizers

    @swagger_auto_schema(
        operation_summary="普通用户登录",
        # operation_description="",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'code': Schema(type=TYPE_STRING),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        """
         weixin api 获取code
        """
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

