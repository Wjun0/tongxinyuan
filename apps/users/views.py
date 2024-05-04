from django.conf import settings
from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from weixin import WXAPPAPI
import jwt
import datetime, base64, time


class LoginAPIVIew(CreateAPIView):
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
        payload = {
            'exp': datetime.datetime.now() + datetime.timedelta(days=1),  # 过期时间
            'iat': datetime.datetime.now(),  #  开始时间
            # 'iss': 'lianzong',  # 签名
            'data': user_info,
        }
        fresh_payload = {
            'exp': datetime.datetime.now() + datetime.timedelta(hours=1),  # 过期时间
            'iat': datetime.datetime.now(),  # 开始时间
            'iss': 'lianzong',  # 签名
            'data': user_info,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(fresh_payload, settings.SECRET_KEY, algorithm='HS256')
        print(token)
        print(refresh_token)
        return Response({"access_token": token, "refresh_token": refresh_token})


