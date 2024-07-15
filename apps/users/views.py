import os

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django_filters import rest_framework
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER, FORMAT_DATETIME
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from weixin import WXAPPAPI
import jwt
import datetime, base64, time, re
from utils.generate_jwt import generate_jwt, jwt_decode
from .filters import UserListerFilter
from .models import User, Media
from drf_yasg.utils import swagger_auto_schema

from .pagenation import ResultsSetPagination
from .permission import LoginPermission, idAdminAndCheckerPermission
from .permission_utils import user_is_checker
from .serializers import UserSerizlizers, MedaiSerializers
import uuid
import io
from django.http import HttpResponse
from qrcode import make as qrcode_make


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
        user_name = data.get('user_name', '')
        pwd = data.get('password', '')
        mobile = data.get('mobile', '')

        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(name):
            return Response({"message": "用户名支持文本与字母数字，不超过20字符"}, status=400)
        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(pwd):
            return Response({"message": "密码支持文本与字母数字，不超过20字符"}, status=400)
        if not re.compile(r'(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$').search(mobile):
            return Response({"message": "手机号格式不正确！"}, status=400)
        if len(name) > 20:
            return Response({"message": "用户名长度超过20个字符！"}, status=400)
        if len(user_name) > 20:
            return Response({"message": "姓名长度超过20个字符！"}, status=400)
        if len(pwd) > 20:
            return Response({"message": "密码长度超过20个字符！"}, status=400)
        if len(pwd) < 6:
            return Response({"message": "密码长度少于6个字符！"}, status=400)
        obj = self.get_queryset().filter(name=name).first()
        if obj:
            if obj.status == "deny": # 已拒绝的可以重新开启
                self.get_queryset().filter(name=name).update(name=name, user_name=user_name, password=pwd, mobile=mobile, status="checking")
                return Response({"message": "注册成功，请等待管理员审核"})
            return Response({"message": "用户名或手机号已注册！"}, status=400)
        user_id = "PC_" + str(uuid.uuid4())
        cre = self.get_queryset().create(user_id=user_id, name=name, user_name=user_name, password=pwd, mobile=mobile, status="checking")
        return Response({"message": "注册成功，请等待管理员审核"})


class UserAddAPIView(CreateAPIView):
    permission_classes = (idAdminAndCheckerPermission, )

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        user_name = data.get('user_name', '')
        pwd = data.get('password', '')
        email = data.get('email', '')
        role = data.get('role')
        tag = data.get('tag')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(name):
            return Response({"message": "用户名支持文本与字母数字，不超过20字符"}, status=400)
        if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(pwd):
            return Response({"message": "密码支持文本与字母数字，不超过20字符"}, status=400)
        # if not re.compile(r'(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$').search(mobile):
        #     return Response({"message": "电话号码格式不正确！"}, status=400)
        if len(name) > 20:
            return Response({"message": "用户名长度超过20个字符！"}, status=400)
        if len(user_name) > 20:
            return Response({"message": "姓名长度超过20个字符！"}, status=400)
        if len(pwd) > 20:
            return Response({"message": "密码长度超过20个字符！"}, status=400)
        if len(pwd) < 6:
            return Response({"message": "密码长度少于6个字符！"}, status=400)
        if tag not in [0,1]:
            return Response({"message": "tag 参数错误！"}, status=400)
        user = User.objects.filter(~Q(role=100)).filter(Q(name=name))
        if user:
            return Response({"message": "用户名已被占用！"},status=400)
        if role:
            if role not in [1,2,3]:
                return Response({"message": "不支持勾选该权限！"}, status=400)
        user_id = "PC_" + str(uuid.uuid4())
        try:
            if tag == 1:
                User.objects.create(user_id=user_id, name=name, user_name=user_name, email=email, password=pwd,
                                    status="used", tag=tag)
            else:
                User.objects.create(user_id=user_id, name=name,user_name=user_name, email=email, password=pwd,
                                    status="pending", tag=tag, start_time=start_time, end_time=end_time)
        except Exception as e:
            return Response({"message": f"添加用户异常！{e}"},status=400)
        return Response({"message": "添加用户成功！"})


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
        obj = self.get_queryset().filter(Q(name=name)).first()
        if not obj:
            return Response({"message": "用户名未注册！"}, status=400)
        if obj.status == "checking":
            return Response({"message": "用户信息审核中！"}, status=400)
        if obj.status == "pending":
            return Response({"message": "用户信息待生效！"}, status=400)
        if obj.status == "deny":
            return Response({"message": "用户注册被拒绝！"}, status=400)

        if obj.password == pwd:
            data = {"user_id": obj.user_id, "iat": time.time()}
            access_token = generate_jwt(data, 1)
            refresh_token = generate_jwt(data, 24)
            obj.token = access_token
            obj.exp_time = datetime.datetime.now()
            obj.save()
            return Response({"message": "ok", "code": 200, "data": {"access_token": access_token, "refresh_token": refresh_token}})
        else:
            return Response({"message": "用户名或密码错误！", "code": 400}, status=400)


class UserAPIView(CreateAPIView, ListAPIView, UpdateAPIView):
    serializer_class = UserSerizlizers
    pagination_class = ResultsSetPagination
    permission_classes = (idAdminAndCheckerPermission, )

    def get_queryset(self):
        queryset = User.objects.filter(~Q(role=100))
        data = self.request.data
        name = data.get('name')
        user_name = data.get('user_name')
        role = data.get('role')
        status = data.get('status')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if user_name:
            queryset = queryset.filter(user_name__icontains=user_name)
        if role:
            queryset = queryset.filter(role__in=role)
        if status:
            queryset = queryset.filter(status__in=status)
        return queryset

    @swagger_auto_schema(
        operation_summary="获取用户列表",
        operation_description="",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'name': Schema(type=TYPE_STRING),
                'user_name': Schema(type=TYPE_STRING),
                'role': Schema(type=TYPE_OBJECT),
                'status': Schema(type=TYPE_OBJECT),
            },
        ),
    )
    def create(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="获取用户详情",
        operation_description="",
    )
    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        user = User.objects.filter(~Q(role=100)).filter(user_id=user_id).first()
        if not user:
            return Response({})
        if user_is_checker and user.role == 1: # 审核人员你能修改管理员数据
            return Response({"message": "不支持操作管理员数据！"}, status=403)
        return Response({"user_name": user.user_name, "name":user.name, "mobile":user.mobile,
                         "role": user.role, "tag": user.tag,"start_time": user.start_time, "end_time": user.end_time})

    @swagger_auto_schema(
        operation_summary="编辑用户信息",
        operation_description="",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'user_id': Schema(type=TYPE_STRING),
                'name': "用户名，不修改不传",
                'user_name': "姓名，不修改不传",
                'mobile': "手机号，不修改不传",
                'tag': "需要立即生效时传1，否则不传",
                'role': "权限， 不修改不传",
                'start_time': "不是立即生效时传递",
                'end_time': "不是立即生效时传递"
            },
        ),
    )
    def put(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id', '')
        name = data.get('name', '')
        user_name = data.get('user_name', '')
        role = data.get('role', '')
        email = data.get('email', '')
        tag = data.get('tag')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        obj = User.objects.filter(~Q(role=100)).filter(user_id=user_id,
                        status__in=["used", "pending", "checking", "deleted"]).first()
        if not obj:
            return Response({"message": "不支持编辑该用户！"}, status=400)
        if name:
            if not re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(name):
                return Response({"message": "用户名支持文本与字母数字，不超过20字符"}, status=400)
            if len(name) > 20:
                return Response({"message": "用户名长度超过20个字符！"}, status=400)
            obj.name = name
        # if mobile:
        #     if not re.compile(r'(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$').search(mobile):
        #         return Response({"message": "电话号码格式不正确！"}, status=400)
        #     obj.mobile = mobile
        if user_is_checker and obj.role == 1: # 审核人员你能修改管理员数据
            return Response({"message": "不支持操作管理员数据！"}, status=403)
        if email:
            obj.email = email
        if user_name:
            if len(user_name) > 20:
                return Response({"message": "姓名长度超过20个字符！"}, status=400)
            obj.user_name = user_name
        if role:
            if role not in [1,2,3]:
                return Response({"message": "不支持勾选该权限！"}, status=400)
            obj.role = role
        if tag == 1:
            obj.tag = 1
        if start_time and end_time:
            obj.tag = 0
            obj.start_time = start_time
            obj.end_time = end_time
        try:
            obj.save()
        except Exception as e:
            return Response({"message": f"data error! {e}"}, status=400)
        return Response({"message": "success "})



class UserAuditAPIView(ListAPIView, CreateAPIView, UpdateAPIView):
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = UserListerFilter
    queryset = User.objects.filter(~Q(role=100))
    serializer_class = UserSerizlizers
    permission_classes = (idAdminAndCheckerPermission, )

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id', '')
        name = data.get('name', '')
        role = data.get('role', '')
        tag = data.get('tag')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        if role not in [1,2,3]:
            return Response({"message": "不支持勾选该权限！"}, status=400)
        obj = get_object_or_404(self.get_queryset(), user_id=user_id, name=name)
        if obj.status != "checking":
            return Response({"message": "用户状态不是待审核！"}, status=400)
        if user_is_checker and obj.role == 1:  # 审核人员你能修改管理员数据
            return Response({"message": "不支持操作管理员数据！"}, status=403)
        obj.role = role
        if tag == 1:
            obj.status = "used"
            obj.tag = 1
        else:
            obj.status = "pending"
            obj.tag = 0
            obj.start_time = start_time
            obj.end_time = end_time
        try:
            obj.save()
        except Exception as e:
            return Response({"message": f"data error! {e}"}, status=400)
        return Response({"message": "success"})

    @swagger_auto_schema(operation_summary="注销|启用 用户", request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'user_id': Schema(type=TYPE_INTEGER),
                'name': Schema(type=TYPE_STRING),
                'status': Schema(type=TYPE_STRING)
            },
        ),)
    def put(self, request, *args, **kwargs):
        """
        注销|启用 用户
        """
        data = request.data
        user_id = data.get('user_id', '')
        status = data.get('status', '')
        if status not in ['used', "pending", 'deleted']:
            return Response({"message": "不支持选择该状态！"}, status=400)
        obj = get_object_or_404(self.get_queryset(), user_id=user_id)
        if obj.status not in ['used', "pending", 'deleted']:
            return Response({"message": "该数据状态不支持修改！"}, status=400)
        if obj.status == "deleted" and status != "used":
            return Response({"message": "只能启用已注销用户！"}, status=400)
        if status == "deleted" and obj.status not in ["used", "pending"]:
            return Response({"message": "只能注销待生效和生效中的用户！"}, status=400)
        if user_is_checker and obj.role == 1: # 审核人员你能修改管理员数据
            return Response({"message": "不支持操作管理员数据！"}, status=403)
        obj.status = status
        obj.save()
        return Response({"message": "success"})


class UserPermissionAPIView(APIView):
    permission_classes = (LoginPermission,)

    @swagger_auto_schema(operation_summary="获取用户权限")
    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
            rule = {"管理员":1, "审核人员":2, "运营人员":3, "其他":100, "错误": 500}
            if obj:
                return Response({"role": obj.role, "rule": rule})
            return Response({"role": 500, "rule": rule},)
        except Exception as e:
            return Response({"message": "permission deny! "}, status=403)


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


class UploadMedioAPIView(CreateAPIView,ListAPIView):
    permission_classes = (idAdminAndCheckerPermission, )

    @swagger_auto_schema(
        operation_summary="上传视频文件",
        # operation_description="",
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'file': Schema(type=TYPE_OBJECT),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        file = request.data.get("file")
        data = request.data
        type = data.get('type', '')
        title = data.get('title', '')
        time_limite = data.get('time_limite', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        desc = data.get('desc', '')
        names = file.name.split('.')
        if names[-1] not in ["mp4", "flv", "avi", "mov", "m4a", "mp3", "wav", "ogg", "asf", "au", "voc", "aiff", "rm", "svcd", "vcd"]:
            return Response({"message":"不支持该文件类型！"}, status=400)
        file_path = f"{str(uuid.uuid4())}.{names[-1]}"
        try:
            with open(os.path.join(settings.BASE_DIR, "media", "qrcode", file_path), 'wb')as f:
                f.write(file.read())
            if time_limite == 1:
                cre = Media.objects.create(title=title, type=type, name=file.name, path=file_path,
                                           time_limite=time_limite, desc=desc)
            else:
                cre = Media.objects.create(title=title, type=type, name=file.name, path=file_path,
                            time_limite=time_limite, start_time=start_time, end_time=end_time, desc=desc)
            return Response({"message": "success", "url": settings.DOMAIN + "user/download/" + file_path})
        except Exception as e:
            return Response({"message": f"bad request! {e}"})



class QRcodeurlView(APIView):
    permission_classes = (idAdminAndCheckerPermission, )
    def get(self, request, *args, **kwargs):
        file_name = kwargs.get('file_name')
        filename = f"media/qrcode/{file_name}"
        path = os.path.join(settings.BASE_DIR, filename)
        if not os.path.exists(path):
            return HttpResponse('File not found.', status=404)
        # 打开文件
        with open(path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
            return response

class ChechUserAPIView(APIView):

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        users = User.objects.filter(~Q(role=100)).filter(name=name)
        if users:
            return Response({"is_used": True})
        return Response({"is_used": False})


class MediaListAPIView(ListAPIView):
    permission_classes = (idAdminAndCheckerPermission, )
    pagination_class = ResultsSetPagination
    serializer_class = MedaiSerializers
    queryset = Media.objects.order_by("-id")
