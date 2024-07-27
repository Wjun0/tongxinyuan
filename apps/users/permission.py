from django.db.models import Q
from rest_framework.permissions import BasePermission
from django.utils import timezone
import datetime
from apps.users.models import User
from utils.generate_jwt import jwt_decode

class FlushPermission(BasePermission):  # 定时任务获取用户信息的认证
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(minutes=2) > now:
                if obj.status == "used":
                    return True
            return False
        except Exception as e:
            return False


class LoginPermission(BasePermission):
    # 登录
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                # if obj.start_time < now < obj.end_time and obj.status == "used":
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False

class isAdminPermission(BasePermission):
    # 管理员权限
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token, role=1).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False


class isCheckerPermission(BasePermission):
    # 审核员权限
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token, role=2).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False

class isOperatorPermission(BasePermission):
    # 运营人员
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token, role=3).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False



class idAdminAndCheckerPermission(BasePermission):
    # 管理员和审核员
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token).filter(Q(role=1) | Q(role=2)).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False


class isManagementPermission(BasePermission):
    # 管理员|审核源|运营人员
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            user_id = data.get("data", {}).get('user_id')
            obj = User.objects.filter(user_id=user_id, token=token, role__lte=3).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(hours=24) > now:
                if obj.status == "used":
                    obj.exp_time = datetime.datetime.now()
                    obj.save()
                    return True
            return False
        except Exception as e:
            return False

