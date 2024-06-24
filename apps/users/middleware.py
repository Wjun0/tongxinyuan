import datetime

from django.http import HttpResponse
from django.utils import timezone
from apps.users.models import User
from utils.generate_jwt import jwt_decode


class AuthenticateDocAccess:
    """
    自定义中间件，用于限制对自动生成API文档的访问
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查是否为文档路径
        if request.path.startswith('/redoc/') or request.path.startswith('/swagger/'):
            # 这里可以根据你的认证方式进行检查，例如使用request.user.is_authenticated
            token = request.META.get('HTTP_AUTHORIZATION')
            try:
                data = jwt_decode(token)
                obj = User.objects.filter(user_id=data.get("data", {}).get('user_id')).first()
                now = timezone.now()
                if obj.token_exp + datetime.timedelta(minutes=15) > now:
                    if obj.start_time < now < obj.end_time and obj.status == "used":
                        pass
            except Exception as e:
                return HttpResponse("未授权访问", status=401)
        response = self.get_response(request)
        return response