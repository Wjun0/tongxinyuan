import datetime
from django.utils import timezone
from apps.users.models import User
from utils.generate_jwt import jwt_decode


def user_is_checker(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    try:
        data = jwt_decode(token)
        obj = User.objects.filter(user_id=data.get("data", {}).get('user_id'), role=2).first()
        now = timezone.now()
        if obj.token_exp + datetime.timedelta(minutes=30) > now and obj.status == "used":
            return True
    except Exception as e:
        return False
    return False