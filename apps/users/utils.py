import re

from apps.users.models import User
from utils.generate_jwt import jwt_decode

def token_to_name(token):
    data = jwt_decode(token)
    user_id = data.get('data',{}).get('user_id')
    obj = User.objects.filter(user_id=user_id).first()
    return obj.name


def count_checking_user(): # 统计待审核人员有多少
    num = User.objects.filter(status="checking").count()
    return num


def check_name_pass(name):
    if re.compile(r'^[a-zA-Z0-9\u4e00-\u9fff]+$').search(name):
        return True
    return False

def check_user_name_pass(user_name):
    if re.compile(r'^[\u4e00-\u9fff]+$').search(user_name):
        return True
    return False

def check_pwd_pass(pwd):
    if not re.search(r'[\u4e00-\u9fff]', pwd):  # 密码不能包含汉字
        return True
    return False

def check_email_pass(email):
    if re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9.-]+$').search(email):
        return True
    return False
