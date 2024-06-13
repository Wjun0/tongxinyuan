from rest_framework.permissions import BasePermission
from django.utils import timezone
import datetime
from apps.users.models import User
from utils.generate_jwt import jwt_decode


class LoginPermission(BasePermission):
    def has_permission(self, request, view):
        token = request.META.get('HTTP_AUTHORIZATION')
        try:
            data = jwt_decode(token)
            obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
            now = timezone.now()
            if obj.token_exp + datetime.timedelta(minutes=15) > now:
                if obj.start_time < now < obj.end_time and obj.status == "used":
                    return True
            return False
        except Exception as e:
            return False


class IsADminPermission(BasePermission):
    def has_permission(self, request, view):
        User.objects.filter()
        return True