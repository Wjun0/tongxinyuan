from django.conf import settings
import jwt
import datetime


def generate_jwt(data, exp):
    payload = {
        'exp': datetime.datetime.now() + datetime.timedelta(hours=exp),  # 过期时间
        'iat': datetime.datetime.now(),  # 开始时间
        'iss': 'tong-psy',  # 签名
        'data': data,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

