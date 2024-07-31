import mimetypes
import os
import random
import string
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django_filters import rest_framework
from drf_yasg.openapi import Schema, TYPE_OBJECT, TYPE_STRING, TYPE_INTEGER, FORMAT_DATETIME
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, get_object_or_404, DestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from weixin import WXAPPAPI
import jwt
import datetime, base64, time, re
from utils.generate_jwt import generate_jwt, jwt_decode
from .filters import UserListerFilter, MediaListerFilter
from .models import User, Media, CheckEmailCode, Document
from drf_yasg.utils import swagger_auto_schema

from .pagenation import ResultsSetPagination
from .permission import LoginPermission, idAdminAndCheckerPermission, isManagementPermission, FlushPermission
from .permission_utils import user_is_checker, user_is_operator, operator_change_data
from .send_email import send
from .serializers import UserSerizlizers, MedaiSerializers
import uuid
from django.utils import timezone
import io
from django.http import HttpResponse
from qrcode import make as qrcode_make

from .utils import token_to_name, count_checking_user, check_user_name_pass, check_name_pass, check_email_pass, check_pwd_pass


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerizlizers
    @swagger_auto_schema(
        request_body=Schema(
            type=TYPE_OBJECT,
            properties={
                'name': Schema(type=TYPE_STRING),
                'password': Schema(type=TYPE_STRING),
                'email': Schema(type=TYPE_STRING)
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
        email = data.get('email')
        code = data.get('code')
        if not check_name_pass(name):
            return Response({"detail": "用户名支持文本与字母数字，不超过20字符"}, status=400)
        if not check_user_name_pass(user_name):
            return Response({"detail": "姓名只支持中文！"}, status=400)
        if not check_pwd_pass(pwd):
            return Response({"detail": "密码仅支持字母、数字、特殊符号!"}, status=400)
        if not check_email_pass(email):
            return Response({"detail": "输入正确的邮箱！"}, status=400)
        if len(name) > 20:
            return Response({"detail": "用户名长度超过20个字符！"}, status=400)
        if len(user_name) > 20:
            return Response({"detail": "姓名长度超过20个字符！"}, status=400)
        if len(pwd) > 20:
            return Response({"detail": "密码长度超过20个字符！"}, status=400)
        if len(pwd) < 6:
            return Response({"detail": "密码长度少于6个字符！"}, status=400)
        obj = CheckEmailCode.objects.filter(email=email, code=code).first()
        now = timezone.now()
        if obj and obj.time + datetime.timedelta(minutes=5) > now:
            pass
        else:
            return Response({"detail": "验证码错误！"}, status=400)

        obj = self.get_queryset().filter(Q(name=name) | Q(email=email)).first()
        if obj:
            if obj.status == "deny": # 已拒绝的可以重新开启
                obj.name = name
                obj.user_name = user_name
                obj.email = email
                obj.password = pwd
                obj.status = "checking"
                obj.save()
                return Response({"detail": "注册成功，请等待管理员审核"})
            return Response({"detail": "用户名或邮箱已注册！"}, status=400)
        user_id = "PC_" + str(uuid.uuid4())
        cre = self.get_queryset().create(user_id=user_id, name=name, user_name=user_name, password=pwd, email=email, status="checking")
        return Response({"detail": "注册成功，请等待管理员审核"})


class UserAddAPIView(CreateAPIView):
    permission_classes = (idAdminAndCheckerPermission, )

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        user_name = data.get('user_name', '')
        pwd = data.get('password', '')
        email = data.get('email', '')
        role = data.get('role', '')
        tag = data.get('tag', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        if not check_name_pass(name):
            return Response({"detail": "用户名支持文本与字母数字，不超过20字符"}, status=400)
        if not check_user_name_pass(user_name):
            return Response({"detail": "姓名只支持中文！"}, status=400)
        if not check_pwd_pass(pwd):
            return Response({"detail": "密码仅支持字母、数字、特殊符号!"}, status=400)
        if not check_email_pass(email):
            return Response({"detail": "输入正确的邮箱！"}, status=400)
        if len(name) > 20:
            return Response({"detail": "用户名长度超过20个字符！"}, status=400)
        if len(user_name) > 20:
            return Response({"detail": "姓名长度超过20个字符！"}, status=400)
        if len(pwd) > 20:
            return Response({"detail": "密码长度超过20个字符！"}, status=400)
        if len(pwd) < 6:
            return Response({"detail": "密码长度少于6个字符！"}, status=400)
        if str(tag) not in ["0", "1"]:
            return Response({"detail": "tag 参数错误！"}, status=400)
        user = User.objects.filter(~Q(role=100)).filter(Q(name=name) | Q(email=email)).first()
        if user:
            if user.status == "deny": # 已拒绝的可以重新开启
                user.name = name
                user.user_name = user_name
                user.email = email
                user.password = pwd
                user.role = role
                user.tag = tag
                if str(tag) == "1":
                    user.status = "used"
                else:
                    user.status = "pending"
                    user.start_time = start_time
                    user.end_time = end_time
                user.save()
                return Response({"detail": "添加用户成功！"})
            return Response({"detail": "用户名已被占用！"},status=400)
        if role:
            if role not in ["1", "2", "3"]:
                return Response({"detail": "不支持勾选该权限！"}, status=400)
        user_id = "PC_" + str(uuid.uuid4())
        try:
            if str(tag) == "1":
                User.objects.create(user_id=user_id, name=name, user_name=user_name, email=email, password=pwd,
                                    status="used", role=role, tag=tag)
            else:
                User.objects.create(user_id=user_id, name=name, user_name=user_name, email=email, password=pwd,
                                    status="pending", role=role, tag=tag, start_time=start_time, end_time=end_time)
        except Exception as e:
            return Response({"detail": f"添加用户异常！{e}"},status=400)
        return Response({"detail": "添加用户成功！"})


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
            return Response({"detail": "用户名未注册！"}, status=400)
        if obj.status == "checking":
            return Response({"detail": "用户信息审核中！"}, status=400)
        if obj.status == "pending":
            return Response({"detail": "用户信息待生效！"}, status=400)
        if obj.status == "deny":
            return Response({"detail": "用户注册被拒绝！"}, status=400)
        if obj.status == "deleted":
            return Response({"detail": "用户名已注销！"}, status=400)
        if obj.password == pwd:
            data = {"user_id": obj.user_id, "iat": time.time()}
            access_token = generate_jwt(data, 24)
            refresh_token = generate_jwt(data, 24)
            obj.token = access_token
            obj.exp_time = datetime.datetime.now()
            obj.save()
            return Response({"detail": "ok", "code": 200, "data": {"access_token": access_token, "refresh_token": refresh_token}})
        else:
            return Response({"detail": "用户名或密码错误！", "code": 400}, status=400)

class LogoutAPIView(APIView):
    permission_classes = (isManagementPermission, )
    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        data = jwt_decode(token)
        obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
        obj.token = "delete"
        obj.save()
        return Response({"detail": "logout success !"})

class ReflushAPIView(APIView):

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        data = jwt_decode(token)
        try:
            obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
            data = {"user_id": obj.user_id, "iat": time.time()}
            access_token = generate_jwt(data, 1)
            refresh_token = generate_jwt(data, 24)
            obj.token = access_token
            obj.exp_time = datetime.datetime.now()
            obj.save()
            return Response({"detail": "ok", "code": 200,
                 "data": {"access_token": access_token, "refresh_token": refresh_token}})
        except Exception as e:
            return Response({"detail": "bad request"}, status=400)


class ForgetPdAPIView(CreateAPIView):
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        pwd1 = data.get('password1', '')
        pwd2 = data.get('password2', '')
        email = data.get('email', '')
        code = data.get('code', '')
        if pwd1 != pwd2:
            return Response({"detail": "两次密码不一致！"}, status=400)
        if not check_pwd_pass(pwd1):
            return Response({"detail": "密码仅支持字母、数字、特殊符号!"}, status=400)
        user = self.get_queryset().filter(name=name).first()
        if not user:
            return Response({"detail": "用户名不存在！"}, status=400)
        if user.email != email:
            return Response({"detail": "邮箱需要与注册邮箱一致！"}, status=400)
        obj = CheckEmailCode.objects.filter(email=email, code=code).first()
        now = timezone.now()
        if obj and obj.time + datetime.timedelta(minutes=5) > now:
            pass
        else:
            return Response({"detail": "验证码错误！"}, status=400)
        if pwd1==user.password or pwd1 in user.old_pwd.get('pwd', []):
            return Response({"detail": "新密码不能与旧密码相同！"}, status=400)
        pwd_list = user.old_pwd.get('pwd', [])
        pwd_list.append(user.password)
        user.old_pwd = {"pwd": pwd_list}
        user.password = pwd1
        user.save()
        return Response({"detail": "success!"})


class CheckPWDandEmailView(CreateAPIView):
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        data = request.data
        name = data.get('name', '')
        pwd = data.get('pwd', '')
        email = data.get('email', '')
        type = data.get('type', '')
        user = self.get_queryset().filter(name=name).first()
        if type == "email":
            if user.email != email:
                return Response({"detail": "邮箱需要与注册邮箱一致！"})
            return Response({"detail": "success"})
        elif type == "pwd":
            if pwd==user.password or pwd in user.old_pwd.get('pwd', []):
                return Response({"detail": "新密码不能与旧密码相同！"})
            return Response({"detail": "success"})
        return Response({"detail": "bad request !"}, status=400)



class UserAPIView(CreateAPIView, ListAPIView, UpdateAPIView):
    serializer_class = UserSerizlizers
    pagination_class = ResultsSetPagination
    permission_classes = (idAdminAndCheckerPermission, )

    def get_queryset(self):
        queryset = User.objects.filter(~Q(role=100)).order_by("-id")
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
        if user_is_checker(request) and user.role == 1: # 审核人员你能修改管理员数据
            return Response({"detail": "不支持操作管理员数据！"}, status=403)
        return Response({"user_name": user.user_name, "name":user.name, "mobile":user.mobile, "email": user.email,
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
            return Response({"detail": "不支持编辑该用户！"}, status=400)
        if name:
            if not check_name_pass(name):
                return Response({"detail": "用户名支持文本与字母数字，不超过20字符"}, status=400)
            if len(name) > 20:
                return Response({"detail": "用户名长度超过20个字符！"}, status=400)
            obj.name = name
        # if mobile:
        #     if not re.compile(r'(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$').search(mobile):
        #         return Response({"detail": "电话号码格式不正确！"}, status=400)
        #     obj.mobile = mobile
        if user_is_checker(request) and obj.role == 1: # 审核人员你能修改管理员数据
            return Response({"detail": "不支持操作管理员数据！"}, status=403)
        if email:
            obj.email = email
        if user_name:
            if len(user_name) > 20:
                return Response({"detail": "姓名长度超过20个字符！"}, status=400)
            if not check_user_name_pass(user_name):
                return Response({"detail": "姓名只支持汉字！"}, status=400)
            obj.user_name = user_name
        if role:
            if role not in ["1", "2", "3"]:
                return Response({"detail": "不支持勾选该权限！"}, status=400)
            obj.role = int(role)
        if str(tag) == "1":  # 立即生效
            obj.tag = 1
            obj.status = "used"
        else:
            obj.tag = 0
            obj.start_time = start_time
            obj.end_time = end_time
            obj.status = "pending"
        try:
            obj.save()
        except Exception as e:
            return Response({"detail": f"data error! {e}"}, status=400)
        return Response({"detail": "success "})



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
        tag = data.get('tag', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        status = data.get('status', '')
        obj = get_object_or_404(self.get_queryset(), user_id=user_id, name=name)
        if not obj:
            return Response({"detail": "用户不存在 !"}, status=400)
        if status == "deny":
            u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
            obj.check_user = u_name
            obj.status = status
            obj.save()
            return Response({"detail": "success !"})
        if role not in ["1" ,"2" ,"3"]:
            return Response({"detail": "不支持勾选该权限！"}, status=400)
        if obj.status != "checking":
            return Response({"detail": "用户状态不是待审核！"}, status=400)
        if user_is_checker(request) and obj.role == 1:  # 审核人员你能修改管理员数据
            return Response({"detail": "不支持操作管理员数据！"}, status=403)
        obj.role = int(role)
        if str(tag) == "1":
            obj.status = "used"
            obj.tag = 1
        else:
            obj.status = "pending"
            obj.tag = 0
            obj.start_time = start_time
            obj.end_time = end_time
        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        obj.check_user = u_name
        try:
            obj.save()
        except Exception as e:
            return Response({"detail": f"data error! {e}"}, status=400)
        return Response({"detail": "success"})

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
            return Response({"detail": "不支持选择该状态！"}, status=400)
        obj = get_object_or_404(self.get_queryset(), user_id=user_id)
        if obj.status not in ['used', "pending", 'deleted']:
            return Response({"detail": "该数据状态不支持修改！"}, status=400)
        if obj.status == "deleted" and status != "used":
            return Response({"detail": "只能启用已注销用户！"}, status=400)
        if obj.status not in ["used", "pending"] and status == "deleted":
            return Response({"detail": "只能注销待生效和生效中的用户！"}, status=400)
        if user_is_checker(request) and obj.role == 1: # 审核人员你能修改管理员数据
            return Response({"detail": "不支持操作管理员数据！"}, status=403)
        obj.status = status
        obj.save()
        return Response({"detail": "success"})


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
                return Response({"role": obj.role, "name": obj.name, "checking": 1,"rule": rule, "user_id": obj.user_id})
            return Response({"role": 500, "rule": rule},)
        except Exception as e:
            return Response({"detail": "permission deny! "}, status=403)


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


class UploadMedioAPIView(CreateAPIView, UpdateAPIView):
    permission_classes = (isManagementPermission, )

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
        file_id = request.data.get("file_id")
        logo = request.data.get("logo")
        data = request.data
        type = data.get('type', '')
        title = data.get('title', '')
        time_limite = data.get('time_limite', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        desc = data.get('desc', '')
        f_name = data.get('name', "")
        if time_limite not in [0, 1, "0", "1"]:
            return Response({"detail": "不支持该限制类型time_limite ！"}, status=400)
        # if names[-1] not in ["mp4", "flv", "avi", "mov", "m4a", "mp3", "wav", "ogg", "asf", "au", "voc", "aiff", "rm", "svcd", "vcd"]:
        #     return Response({"detail":"不支持该文件类型！"}, status=400)
        uid = ""
        logo_path = ""
        if logo:
            l_names = logo.name.split('.')
            if l_names[-1] not in ["png", "jpg"]:
                return Response({"detail": "不支持该文件类型！"}, status=400)
            uid = str(uuid.uuid4())
            logo_path = f"{uid}.{l_names[-1]}"
            with open(os.path.join(settings.BASE_DIR, "media", "logo", logo_path), 'wb')as f:
                f.write(logo.read())

        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        f = Document.objects.filter(docfile=file_id).first()
        if not f:
            return Response({"detail":"不支持的file_id"}, status=400)
        try:
            now = datetime.datetime.now()
            if str(time_limite) == "1":
                cre = Media.objects.create(title=title, type=type, name=f_name, path=f.filename, file_id=f.docfile,
                                           user=u_name, create_time=now, update_time=now,
                                           logo_id=uid, logo_name=logo_path, time_limite=time_limite,
                                           start_time=start_time, end_time=end_time, desc=desc)
            else:
                cre = Media.objects.create(title=title, type=type, name=f_name, path=f.filename, user=u_name,
                                           logo_id=uid, logo_name=logo_path, file_id=f.docfile, time_limite=time_limite,
                                           desc=desc, create_time=now, update_time=now)
            return Response({"detail": "success", "url": settings.DOMAIN + "/user/download/" + file_id})
        except Exception as e:
            return Response({"detail": f"bad request! {e}"}, status=400)

    def put(self, request, *args, **kwargs):
        data = request.data
        file_id = data.get('file_id')
        file_name = data.get('file_name')
        try:
            f = Media.objects.filter(file_id=file_id).first()
            if not f:
                return Response({"detail": "File not found."}, status=404)
            f.name = file_name
            f.update_time = datetime.datetime.now()
            f.save()
            return Response({"detail": "success", "file_name": file_name})
        except Exception as e:
            return Response({"detail": "bad request !"}, status=400)


class UploadUrlMedioAPIView(CreateAPIView, UpdateAPIView):
    permission_classes = (isManagementPermission,)
    queryset = Media.objects.all()

    def create(self, request, *args, **kwargs):
        logo = request.data.get("logo")
        data = request.data
        original_url = data.get('original_url')
        title = data.get('title', '')
        name = data.get('name', '')
        desc = data.get('desc', '')
        time_limite = data.get('time_limite', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        uid = ""
        logo_path = ""
        now = datetime.datetime.now()
        name = name if name else f"{now.strftime('%Y%m%d')}{random.randint(1111,9999)}{''.join(random.choices(string.ascii_lowercase, k=2))}"
        if time_limite not in [0, 1, "0", "1"]:
            return Response({"detail": "不支持该限制类型time_limite ！"}, status=400)
        if not original_url:
            return Response({"detail": "origin_url 必传！"}, status=400)
        if logo:
            l_names = logo.name.split('.')
            if l_names[-1] not in ["png", "jpg"]:
                return Response({"detail": "不支持该文件类型！"}, status=400)
            uid = str(uuid.uuid4())
            logo_path = f"{uid}.{l_names[-1]}"
            with open(os.path.join(settings.BASE_DIR, "media", "logo", logo_path), 'wb')as f:
                f.write(logo.read())
        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        file_id = str(uuid.uuid4())
        try:
            now = datetime.datetime.now()
            if str(time_limite) == "1":
                cre = Media.objects.create(title=title, type="url", name=name, path="", user=u_name,
                                           original_url=original_url,
                                           logo_id=uid, logo_name=logo_path, file_id=file_id, time_limite=time_limite,
                                           start_time=start_time, end_time=end_time,
                                           desc=desc, create_time=now, update_time=now)
            else:
                cre = Media.objects.create(title=title, type="url", name=name, path="", user=u_name, original_url=original_url,
                                           logo_id=uid, logo_name=logo_path, file_id=file_id, time_limite=time_limite,
                                           desc=desc, create_time=now, update_time=now)
            return Response({"detail": "success", "url": settings.DOMAIN + "/user/download/" + file_id})
        except Exception as e:
            return Response({"detail": f"bad request! {e}"}, status=400)

    def put(self, request, *args, **kwargs):
        data = request.data
        file_id = data.get('file_id')
        original_url = data.get('original_url')
        try:
            f = Media.objects.filter(file_id=file_id).first()
            if not f:
                return Response({"detail": "File not found."}, status=404)
            if user_is_operator(request):  # 如果是运营人员，判断是否有权限
                if not operator_change_data(request, f):
                    return Response({"detail": "没有权限操作该数据！"}, status=403)
            f.original_url = original_url
            f.update_time = datetime.datetime.now()
            f.save()
            return Response({"detail": "success", "original_url": original_url})
        except Exception as e:
            return Response({"detail": "bad request !"}, status=400)


class UploadLogoAPIView(CreateAPIView):
    permission_classes = (isManagementPermission,)
    queryset = Media.objects.all()

    def post(self, request, *args, **kwargs):
        file = request.data.get("file")
        data = request.data
        file_id = data.get('file_id', '')
        names = file.name.split('.')
        if names[-1] not in ["png", "jpg"]:
            return Response({"detail": "不支持该文件类型！"}, status=400)
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found !"}, status=400)
        uid = str(uuid.uuid4())
        file_path = f"{uid}.{names[-1]}"
        with open(os.path.join(settings.BASE_DIR, "media", "logo", file_path), 'wb')as f:
            f.write(file.read())
        obj.logo_id = uid
        obj.logo_name = file_path
        f.update_time = datetime.datetime.now()
        obj.save()
        return Response({"detail": "success ", "logo_id": uid, "url": settings.DOMAIN + "/user/download_logo/" + uid})

class UploadQRcodeAPIView(CreateAPIView, UpdateAPIView):
    permission_classes = (isManagementPermission,)
    queryset = Media.objects.all()
    def post(self, request, *args, **kwargs):
        file = request.data.get("file")
        data = request.data
        file_id = data.get('file_id', '')
        qrcode_size = data.get('qrcode_size', '')
        qrcode_shape = data.get('qrcode_shape', '')
        qrcode_site = data.get('qrcode_site', '')
        names = file.name.split('.')
        if names[-1] not in ["png", "jpg"]:
            return Response({"detail": "不支持该文件类型！"}, status=400)
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found !"}, status=400)
        uid = str(uuid.uuid4())
        file_path = f"{uid}.{names[-1]}"
        with open(os.path.join(settings.BASE_DIR, "media", "logo", file_path), 'wb')as f:
            f.write(file.read())
        obj.qrcode_id = uid
        obj.qrcode_name = file_path
        obj.qrcode_size = qrcode_size
        obj.qrcode_shape = qrcode_shape
        obj.qrcode_site = qrcode_site
        obj.update_time = datetime.datetime.now()
        obj.save()
        return Response({"detail": "success ", "qrcode_id": uid, "url": settings.DOMAIN + "/user/download_qrcode/" + uid})

    def put(self, request, *args, **kwargs):
        data = request.data
        file_id = data.get('file_id', '')
        qrcode_size = data.get('qrcode_size', '')
        qrcode_shape = data.get('qrcode_shape', '')
        qrcode_site = data.get('qrcode_site', '')
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found !"}, status=400)
        obj.qrcode_size = qrcode_size
        obj.qrcode_shape = qrcode_shape
        obj.qrcode_site = qrcode_site
        obj.update_time = datetime.datetime.now()
        obj.save()
        return Response({"detail": "success "})


class QRcodeurlView(APIView):
    # permission_classes = (idAdminAndCheckerPermission, )
    def get(self, request, *args, **kwargs):
        file_id = kwargs.get('file_id')
        f = Media.objects.filter(file_id=file_id).first()
        if not f:
            return Response({"detail": "File not found."}, status=404)
        filename = f"media/qrcode/{f.path}"
        path = os.path.join(settings.BASE_DIR, filename)
        if not os.path.exists(path):
            return Response({"detail": "File not found."}, status=404)
        # 打开文件
        with open(path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mimetypes.guess_type(path)[0])
            response['Content-Disposition'] = 'attachment; filename=' + f.name
            return response

class DownloadLogoView(APIView):
    # permission_classes = (idAdminAndCheckerPermission,)

    def get(self, request, *args, **kwargs):
        logo_id = kwargs.get('logo_id')
        f = Media.objects.filter(logo_id=logo_id).first()
        if not f:
            return Response({"detail": "File not found."}, status=404)
        filename = f"media/logo/{f.logo_name}"
        path = os.path.join(settings.BASE_DIR, filename)
        if not os.path.exists(path):
            return Response({"detail": "File not found."}, status=404)
        # 打开文件
        with open(path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mimetypes.guess_type(path)[0])
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
            return response

class DownloadQrcodeView(APIView):

    def get(self, request, *args, **kwargs):
        qrcode_id = kwargs.get('qrcode_id')
        f = Media.objects.filter(qrcode_id=qrcode_id).first()
        if not f:
            return Response({"detail": "File not found."}, status=404)
        filename = f"media/logo/{f.qrcode_name}"
        path = os.path.join(settings.BASE_DIR, filename)
        if not os.path.exists(path):
            return Response({"detail": "File not found."}, status=404)
        # 打开文件
        with open(path, 'rb') as file:
            response = HttpResponse(file.read(), content_type=mimetypes.guess_type(path)[0])
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(path)
            return response


class ChechUserAPIView(APIView):

    def get(self, request, *args, **kwargs):
        name = request.query_params.get("name")
        users = User.objects.filter(~Q(role=100)).filter(name=name)
        if users:
            return Response({"is_used": True})
        return Response({"is_used": False})


class ChechEmailAPIView(APIView):

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        users = User.objects.filter(~Q(role=100)).filter(email=email).first()
        if users:
            if users.status != "deny":
                return Response({"is_used": True})
        return Response({"is_used": False})


class SendEmailAPIView(APIView):

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if not check_email_pass(email):
            return Response({"detail": "输入正确的邮箱！"}, status=400)
        code = random.randint(111111, 999999)
        try:
            obj = CheckEmailCode.objects.filter(email=email).first()
            now = timezone.now()
            if obj:
                if obj.time + datetime.timedelta(minutes=1) > now:
                    return Response({"detail": "请勿频繁发送！"}, status=403)
            data = {"email": email, "code": code, "time": now}
            cre = CheckEmailCode.objects.update_or_create(email=email, defaults=data)
            send(email, code)
            return Response({"detail": "success! "})
        except Exception as e:
            return Response({"detail": "bad request !"}, status=400)


class MediaListAPIView(ListAPIView):
    permission_classes = (isManagementPermission, )
    filterset_class = MediaListerFilter
    pagination_class = ResultsSetPagination
    serializer_class = MedaiSerializers
    queryset = Media.objects.order_by("-update_time")


class MediaDetailAPIView(ListAPIView, CreateAPIView, UpdateAPIView):
    permission_classes = (isManagementPermission, )
    serializer_class = MedaiSerializers
    queryset = Media.objects.order_by("-id")

    def list(self, request, *args, **kwargs):
        file_id = request.query_params.get("file_id")
        f = self.get_queryset().filter(file_id=file_id).first()
        if not f:
            return Response({"detail": "File not found."}, status=404)
        ser = self.get_serializer(f)
        return Response(ser.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        time_limite = data.get('time_limite', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        file_id = data.get('file_id', '')
        new_file_id  = data.get('new_file_id', '')
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found."}, status=404)
        if user_is_operator(request):  # 如果是运营人员，判断是否有权限
            if not operator_change_data(request, obj):
                return Response({"detail": "没有权限操作该数据！"}, status=403)
        f = Document.objects.filter(docfile=new_file_id).first()
        if not f:
            return Response({"detail": "不支持的new_file_id"}, status=400)
        try:
            obj.name = f.filename
            obj.path = f.filename
            obj.update_time = timezone.now()
            if str(time_limite) == "1":
                obj.time_limite = time_limite
                obj.start_time = start_time
                obj.end_time = end_time
            else:
                obj.time_limite = 0
            obj.save()
            return Response({"detail": "success"})
        except Exception as e:
            return Response({"detail": "bad request !"}, status=400)

    def put(self, request, *args, **kwargs):
        data = request.data
        time_limite = data.get('time_limite', '')
        start_time = data.get('start_time', '')
        end_time = data.get('end_time', '')
        file_id = data.get('file_id', '')
        type = data.get('type', '')
        new_file_id = data.get('new_file_id', '')
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found."}, status=404)
        if user_is_operator(request):  # 如果是运营人员，判断是否有权限
            if not operator_change_data(request, obj):
                return Response({"detail": "没有权限操作该数据！"}, status=403)
        if type == "update_file":
            if new_file_id:
                d = Document.objects.filter(docfile=new_file_id).first()
                if not d:
                    return Response({"detail": "New File not found."}, status=404)
                obj.path = d.filename
                obj.update_time = datetime.datetime.now()
                obj.save()
                return Response({"detail": "success"})
            else:
                return Response({"message": "new_file_id 不能为空！"}, status=400)
        try:
            if str(time_limite) == "1":
                obj.time_limite = 1
                obj.start_time = start_time
                obj.end_time = end_time
            else:
                obj.time_limite = 0
            obj.update_time = timezone.now()
            obj.save()
            return Response({"detail": "success"})
        except Exception as e:
            return Response({"detail": "bad request !"}, status=400)

class MediaDeleteAPIView(CreateAPIView):
    permission_classes = (isManagementPermission,)
    serializer_class = MedaiSerializers
    queryset = Media.objects.order_by("-id")

    def create(self, request, *args, **kwargs):
        data = request.data
        file_id = data.get('file_id', '')
        type = data.get('type', '')
        obj = self.get_queryset().filter(file_id=file_id).first()
        if not obj:
            return Response({"detail": "File not found."}, status=404)
        if user_is_operator(request):  # 如果是运营人员，判断是否有权限
            if not operator_change_data(request, obj):
                return Response({"detail": "没有权限操作该数据！"}, status=403)
        if type == "logo":
            try:
                logo_name = obj.logo_name
                p = os.path.join(settings.BASE_DIR, "media", "logo", logo_name)
                os.remove(p)
                obj.logo_id = ""
                obj.logo_name = ""
                obj.save()
                return Response({"detail": "success"})
            except Exception as e:
                return Response({"detail": "文件不存在！"}, status=400)
        elif type == "qrcode":
            try:
                p = os.path.join(settings.BASE_DIR, "media", "logo", obj.qrcode_name)
                os.remove(p)
                obj.qrcode_name = ""
                obj.qrcode_id = ""
                obj.save()
                return Response({"detail": "success"})
            except Exception as e:
                return Response({"detail": "文件不存在！"}, status=400)
        elif type == "media":
            try:
                path = obj.path
                logo_name = obj.logo_name
                qrcode_name = obj.qrcode_name
                if logo_name:
                    p = os.path.join(settings.BASE_DIR, "media", "logo", logo_name)
                    os.remove(p)
                if qrcode_name:
                    p = os.path.join(settings.BASE_DIR, "media", "logo", qrcode_name)
                    os.remove(p)
                p = os.path.join(settings.BASE_DIR, "media", "qrcode", path)
                os.remove(p)
                obj.delete()
                return Response({"detail": "success"})
            except Exception as e:
                return Response({"detail": "文件不存在！"}, status=400)
        elif type == "url":
            obj.delete()
            return Response({"detail": "success"})
        return Response({"detail": "bad request"}, 400)


class UserInfoAPIView(APIView):
    permission_classes = (FlushPermission,)

    def get(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
            if obj:
                mun = count_checking_user() if obj.role in [1, 2] else 0
                return Response({"role": obj.role, "name": obj.name, "email": obj.email, "checking_num": mun})
            return Response({"detail": "user not found !"}, status=400)
        except Exception as e:
            return Response({"detail": "permission deny! "}, status=403)

