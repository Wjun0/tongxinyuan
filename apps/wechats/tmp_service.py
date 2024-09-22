from django.conf import settings

from apps.questions.models import QuestionType_tmp, Question_tmp, Option_tmp
from apps.users.exceptions import Exception_
from apps.wechats.models import UserAnswer_tmp
from apps.wechats.services import generate_tmp_result


def get_tmp_result(qt_id):
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if not qt:
        raise Exception_("问卷不存在！")
    background_img = qt.background_img
    if background_img:
        background_img = settings.DOMAIN + "/media/image/" + background_img
    title_img = qt.title_img
    if title_img:
        title_img = settings.DOMAIN + "/media/image/" + title_img
    result = {"qt_id": qt.u_id, "background_img": background_img, 'title_img': title_img,
              "title": qt.title, "test_value": qt.test_value, "test_value_html": qt.test_value_html,
              'q_number': qt.q_number, "test_time": qt.test_time, "use_count": qt.use_count, 'source': qt.source}
    return result

def get_user_tmp_answer_result(data, user_id):
    qt_id = data.get('u_id', '')
    ans_id = data.get('ans_id', '')
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if not qt:
        title = ''
    else:
        title = qt.title
    if not ans_id:  # 没有ans_id 获取历史的问卷结果
        obj = UserAnswer_tmp.objects.filter(qt_id=qt_id, user_id=user_id).order_by('-update_time').first()
        if not obj:
            result = {}
        else:
            result = obj.result
        return {"detail": "success", "data": result, 'title': title}
    # 统计完成数据,必须在生成结果前统计
    # count_finish_number(user_id, qt_id, ans_id)
    generate_tmp_result(qt_id, ans_id)
    # 生成结果
    obj = UserAnswer_tmp.objects.filter(u_id=ans_id, qt_id=qt_id).first()
    if not obj:
        result = {}
    else:
        result = obj.result
    return {"detail": "success", "data": result, 'title': title}