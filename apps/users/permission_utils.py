import datetime
from django.utils import timezone
from apps.users.models import User
from utils.generate_jwt import jwt_decode


def user_is_checker(request): # 是审核人员
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        data = jwt_decode(token)
        user_id = data.get("data", {}).get('user_id')
        obj = User.objects.filter(user_id=user_id, role=2).first()
        now = timezone.now()
        if obj.token_exp + datetime.timedelta(hours=24) > now and obj.status == "used":
            return True
    except Exception as e:
        return False
    return False


def user_is_operator(request): # 是运营人员
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        data = jwt_decode(token)
        user_id = data.get("data", {}).get('user_id')
        obj = User.objects.filter(user_id=user_id, role=3).first()
        now = timezone.now()
        if obj.token_exp + datetime.timedelta(hours=24) > now and obj.status == "used":
            return True
    except Exception as e:
        return False
    return False


def operator_change_data(request, media):  # 运营人员只能修改自己数据权限
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        data = jwt_decode(token)
        obj = User.objects.filter(user_id=data.get("data", {}).get('user_id'), role=3).first()
        now = timezone.now()
        if obj.token_exp + datetime.timedelta(hours=24) > now and obj.status == "used":
            if obj.name == media.user:
                return True
            return False
    except Exception as e:
        return False
    return False