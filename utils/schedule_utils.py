import os
import shutil
from datetime import datetime
from pathlib import Path

from django.db.models import Q

from apps.questions.models import QuestionType_tmp, QuestionType
from apps.questions.services import copy_tmp_table
from apps.users.models import User
from django.utils import timezone

def update_user_status():
    users = User.objects.filter(tag=0, status__in=["used", "pending"]).filter(~Q(role=100))
    for i in users:
        now = timezone.now()
        if i.status == "used":  # 生效中的
            if i.start_time < now < i.end_time:
                pass
            else:
                i.status = "deleted"
                i.save()
        else:
            if i.start_time < now < i.end_time:
                i.status = "used"
                i.save()
            elif i.start_time < now and i.end_time < now:
                i.status = "deleted"
                i.save()
    return

def update_question_status():
    # 更新问卷状态
    ques = QuestionType_tmp.objects.filter(status_tmp="待生效")
    for i in ques:
        now = timezone.now()
        if i.start_time < now < i.end_time:
            i.status_tmp = "已上线"
            i.status = "已上线"
            i.save()
            copy_tmp_table(i.u_id) # 同步表

    ques = QuestionType_tmp.objects.filter(status_tmp="已上线")
    for i in ques:
        now = timezone.now()
        if not(i.start_time < now < i.end_time):
            i.status_tmp = "已失效"
            i.status = "已失效"
            i.save()
            QuestionType.objects.filter(u_id=i.u_id).update(status_tmp="已失效", status="已失效")
            #copy_tmp_table(i.u_id)
    return


def backup_data():
    d = datetime.now()
    year = str(d.year)
    month = str(d.month)
    day = str(d.day)
    new_name = f'tong-psy_bak_{year}-{month}-{day}'
    # 备份代码文件
    BASE_PATH = Path(__file__).resolve().parent.parent.parent
    old_file = os.path.join(BASE_PATH, 'tong-psy')
    new_file = os.path.join(BASE_PATH, new_name)
    if not os.path.exists(new_file): # 不存在就备份
        shutil.copytree(old_file, new_file)

    # 删除历史备份
    dir_list = os.listdir(BASE_PATH)
    for i in dir_list:
        if i.startswith('tong-psy_bak_'):
            if i != new_name:
                print(i)
                d = os.path.join(BASE_PATH, i)
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    pass
    return
