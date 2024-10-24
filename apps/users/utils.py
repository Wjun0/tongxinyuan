import re

from apps.questions.models import QuestionType_tmp, Channel_tmp
from apps.users.models import User
from utils.generate_jwt import jwt_decode

def token_to_name(token):
    data = jwt_decode(token)
    user_id = data.get('data',{}).get('user_id')
    obj = User.objects.filter(user_id=user_id).first()
    return obj.name

def get_user_id(token):
    data = jwt_decode(token)
    user_id = data.get('data', {}).get('user_id')
    return user_id

def count_checking_user(): # 统计待审核人员有多少
    num = User.objects.filter(status="checking").count()
    return num

def count_checking_question(): # 统计有多少待审核的问卷
    num = QuestionType_tmp.objects.filter(status_tmp__in=["待审核", '已上线（草稿待审核）']).count()
    return num

def count_checking_channel(): # 统计有多少待审核的频道
    num = Channel_tmp.objects.filter(status__in=["待审核", '已上线（草稿待审核）']).count()
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
