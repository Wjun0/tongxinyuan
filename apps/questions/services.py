import uuid

from apps.questions.check_data_service import check_start_end_time, check_img
from apps.questions.models import Question, Option, Calculate_Exp, Question_tmp, Option_tmp, Calculate_Exp_tmp, \
    Result_Title, Result_Title_tmp, Dimension, Dimension_tmp, QuestionType_tmp
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
                  "q_title": q.get('q_title'), "q_title_html": q.get('q_title_html') ,"q_check_role": q.get('q_check_role')}
        cre = Question_tmp.objects.create(**q_data)
        cre = Question.objects.create(**q_data)
        a_data_list = []
        for a in q.get('q_options'):
            a_uid = str(uuid.uuid4())
            a_data = {"u_id": a_uid, "q_id": q_uid, "o_number": a.get('o_number'), "o_content": a.get('o_content'), "o_html_content": a.get('o_html_content')}
            an_cre = Option_tmp.objects.create(**a_data)
            an_cre = Option.objects.create(**a_data)
            a_data_list.append({"u_id": a_uid, "q_id": an_cre.q_id, "o_number": an_cre.o_number,
                                 "o_content": an_cre.o_content, "o_html_content": an_cre.o_html_content})
        res.append({"q_id": cre.u_id, "qt_id": cre.qt_id, "number": cre.number, "q_type":cre.q_type,
                    "q_attr": cre.q_attr, "q_title": cre.q_attr, "q_check_role": cre.q_check_role,
                    "options": a_data_list})
            # a_data_list.append(Answer(**a_data))
        # an = Answer.objects.bulk_create(a_data_list)
        # print(an)

    return res

def get_option_data(request):
    qt_id = request.query_params.get("qt_id")
    ques = Question_tmp.objects.filter(qt_id=qt_id)
    result = []
    for q in ques:
        ops = Option_tmp.objects.filter(q_id=q.u_id)
        ops_list = []
        for op in ops:
            ops_list.append({"o_number": op.o_number, "value": op.value})
        result.append({"q_id": q.u_id, "number": q.number, "q_check_role": q.q_check_role, "options": ops_list})
    return result



def add_order_and_select_value(request):
    data = request.data
    order = data.get('order')
    values = data.get('values')
    for i in order:
        Option.objects.filter(q_id=i.get('q_id'), o_number=i.get('o_number')).update(next_q_id=i.get('next_q_id'))
        Option_tmp.objects.filter(q_id=i.get('q_id'), o_number=i.get('o_number')).update(next_q_id=i.get('next_q_id'))
    for j in values:
        Option.objects.filter(q_id=j.get('q_id'), o_number=j.get('o_number')).update(value=j.get('value'))
        Option_tmp.objects.filter(q_id=j.get('q_id'), o_number=j.get('o_number')).update(value=j.get('value'))
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

def add_result(request):
    data = request.data
    qt_id = data.get('qt_id')
    results = data.get('results')
    for r in results:
        uid = str(uuid.uuid4())
        res = {"u_id": uid, "qt_id": qt_id, "statement": r.get('statement', ''),
               "background_img": r.get('background_img',''), "result_img": r.get('result_img', '')}
        Result_Title.objects.create(**res)
        Result_Title_tmp.objects.create(**res)
        for dim in r.get('dimession', []):
            dimension_number = dim.get('dimension_number', '')
            dimension_name = dim.get('dimension_name', '')
            d_result = dim.get('d_result', [])
            for j in d_result:
                result_number = j.get('result_number', '')
                result_name = j.get('result_name', '')
                result_desc = j.get('result_desc', '')
                value = j.get('value', {})
                dim_u_id = str(uuid.uuid4())
                dim_data = {"u_id": dim_u_id, 'qt_id': qt_id, 'r_id': uid, "dimension_number": dimension_number,
                            "dimension_name": dimension_name, "result_number": result_number,
                            "result_name": result_name, "result_desc": result_desc, "value":value}
                Dimension.objects.create(**dim_data)
                Dimension_tmp.objects.create(**dim_data)
    return


def show_result(request):
    data = request.data
    qt_id = data.get('qt_id')
    result = {}
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if qt:
        step1 = {"start_time": qt.start_time, "end_time": qt.end_time, "background_img": qt.background_img, 'title_img': qt.title_img,
             "title":qt.title, "test_value": qt.test_value, "q_number": qt.q_number, "test_time": qt.test_time,
             "use_count": qt.use_count, "source": qt.source}
        result["step1"] = step1
        ques = Question_tmp.objects.filter(qt_id=qt_id)
        questions = []
        order = []
        for i in ques:
            q_id = i.u_id
            ans = Option_tmp.objects.filter(q_id=q_id)
            options = []
            for j in ans:
                options.append({"o_number": j.o_number, "o_content": j.o_content})
                if j.next_q_id:
                    next = Option_tmp.objects.filter(q_id=j.next_q_id).first()
                    order.append({"q_id": q_id, "number": i.number, "o_number": j.o_number,
                                  "next_q_id": next.u_id, "next_number": next.number})
            questions.append({"number": i.number, "q_title": i.q_title, "answers": options})
        result["step2"] = questions
        exp_list = []
        exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
        for m in exps:
            exp_list.append({"exp_name": m.exp_name, "exp": m.exp})
        result['step3'] = {"orders": order, "exps": exp_list}

        step4 = []
        res = Result_Title_tmp.objects.filter(qt_id=qt_id)
        for i in res:
            r_id = i.u_id
            background_img = i.background_img
            statement = i.statement
            result_img = i.result_img
            dims = Dimension_tmp.objects.filter(qt_id=qt_id, r_id=r_id)
            dimension_dic = {}
            for j in dims:
                dimension_dic[j.dimension_number] = j.dimension_name
            dimensions = []
            for m, v in dimension_dic:
                ds = Dimension_tmp.objects.filter(qt_id=qt_id, r_id=r_id, dimension_number=m)
                res_list = []
                for d in ds:
                    r_d = {"result_number": d.result_number, "result_name": d.result_name,
                           "result_desc": d.result_desc, "value": d.value}
                    res_list.append(r_d)
                s = {"dimension_number": m, "dimension_name":v, "d_result": res_list}
                dimensions.append(s)
            dim_tp = {"background_img":background_img, "statement":statement, "result_img":result_img, "dimensions": dimensions}
            step4.append(dim_tp)
        result["step4"] = step4





    return result