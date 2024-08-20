import uuid

from apps.questions.check_data_service import check_start_end_time, check_img
from apps.questions.models import Question, Answer, Calculate_Exp, Question_tmp, Answer_tmp, Calculate_Exp_tmp
from apps.users.exceptions import Exception_


def add_question_type(request):
    data = request.data
    background_img = data.get('background_img')
    title_img = data.get('title_img')
    title = data.get('title')
    test_value = data.get('test_value')
    q_number = data.get('q_number')
    test_time = data.get('test_time')
    use_count = data.get('use_count')
    source = data.get('source')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    if not check_start_end_time(start_time, end_time):
        raise Exception_("时间格式错误！")
    if background_img:
        if not check_img(background_img, "background_img"):
            raise Exception_("背景图校验错误！")
    if not check_img(title_img, "title_img"):
        raise Exception_("主图校验错误！")
    # if not(isinstance(q_number, int) and q_number > 0):
    #     raise Exception_("题目个数只支持正整数！")
    if not(isinstance(use_count, int) and use_count > 0):
        raise Exception_("已参与人数只支持正整数！")
    # try:
    #     float(test_time)
    # except Exception as e:
    #     raise Exception_("预计用时只支持数字（支持小数）")
    if len(title) > 18:
        raise Exception_("问卷标题不超过18个字!")
    return True

def add_question(request):
    data = request.data
    qt_id = data.get("qt_id")
    questions = data.get('questions')
    res = []
    for q in questions:
        q_uid = str(uuid.uuid4())
        q_data = {"u_id": q_uid,"number": q.get('number'), "qt_id": qt_id, "q_type": q.get('q_type'), "q_attr": q.get('q_attr'),
                  "q_title": q.get('q_title'), "q_check_role": q.get('q_check_role')}
        cre = Question_tmp.objects.create(**q_data)
        cre = Question.objects.create(**q_data)
        a_data_list = []
        for a in q.get('answer'):
            a_uid = str(uuid.uuid4())
            a_data = {"u_id": a_uid, "q_id": q_uid, "a_number": a.get('a_number'), "a_answer": a.get('a_answer')}
            an_cre = Answer_tmp.objects.create(**a_data)
            an_cre = Answer.objects.create(**a_data)
            a_data_list.append({"id": an_cre.id, "q_id": an_cre.q_id,
                                "a_number": an_cre.a_number, "a_answer": an_cre.a_answer})
        res.append({"q_id": cre.u_id, "qt_id": cre.qt_id, "number": cre.number, "q_type":cre.q_type,
                    "q_attr": cre.q_attr, "q_title": cre.q_attr, "q_check_role": cre.q_check_role,
                    "answer": a_data_list})
            # a_data_list.append(Answer(**a_data))
        # an = Answer.objects.bulk_create(a_data_list)
        # print(an)

    return res


def add_order_and_select_value(request):
    data = request.data
    order = data.get('order')
    values = data.get('values')
    for i in order:
        Answer.objects.filter(q_id=i.get('q_id'), a_number=i.get('a_number')).update(next_q_id=i.get('next_q_id'))
        Answer_tmp.objects.filter(q_id=i.get('q_id'), a_number=i.get('a_number')).update(next_q_id=i.get('next_q_id'))
    for j in values:
        Answer.objects.filter(q_id=j.get('q_id'), a_number=j.get('a_number')).update(value=j.get('value'))
        Answer_tmp.objects.filter(q_id=j.get('q_id'), a_number=j.get('a_number')).update(value=j.get('value'))
    return

def add_calculate(request):
    data = request.data
    qt_id = data.get('qt_id')
    exp = data.get('exp')
    for i in exp:
        i['qt_id'] = qt_id
        Calculate_Exp.objects.create(**i)
        Calculate_Exp_tmp.objects.create(**i)
    return
