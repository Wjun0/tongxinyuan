from datetime import datetime

from apps.questions.models import Image
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

