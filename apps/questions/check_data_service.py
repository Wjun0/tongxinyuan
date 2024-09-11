from datetime import datetime

from apps.questions.models import Image, QuestionType_tmp
from apps.users.exceptions import Exception_


def check_start_end_time(start_time, end_time):
    try:
        s = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')  # 根据实际情况调整日期时间格式
        e = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')  # 根据实际情况调整日期时间格式
        if s < e:
            return True
        raise Exception_("开始时间必须小于结束时间！")
    except ValueError:
        raise Exception_("时间格式不正确！")


def check_img(img_id, type):
    obj = Image.objects.filter(file_id=img_id, source=type).first()
    if not obj:
        raise Exception_("文件不存在！")
    return True


def check_add_question(data):
    qt_id = data.get("qt_id")
    questions = data.get('questions')
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if not qt:
        raise Exception_('问卷不存在！')
    index = 1
    for i in questions:
        number = i.get('number')
        try:
            if int(number) != index:
                raise Exception_(f'问题编号{index}错误！')
            index += 1
        except Exception as e:
            raise Exception_(f'不支持该题目编号{number}！')