from django.conf import settings
import jwt
import datetime


def generate_jwt(data, exp):
    payload = {
        'exp': datetime.datetime.now() + datetime.timedelta(hours=exp),  # 过期时间
        # 'iat': datetime.datetime.now(),  # 开始时间
        # 'iss': 'tong-psy',  # 签名
        'data': data,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def jwt_decode(token):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return payload


if __name__ == '__main__':
    token = generate_jwt({"user_id": "12345"}, 1)
    jwt_decode(token)

