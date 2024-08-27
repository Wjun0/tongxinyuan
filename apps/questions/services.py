import uuid

from django.db.models import Q

from apps.questions.check_data_service import check_start_end_time, check_img
from apps.questions.models import Question, Option, Calculate_Exp, Question_tmp, Option_tmp, Calculate_Exp_tmp, \
    Result_Title, Result_Title_tmp, Dimension, Dimension_tmp, QuestionType_tmp, QuestionType
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
    del_q_id = []  # 删除使用
    for q in questions:
        q_id = q.get('q_id')
        q_data = {"number": q.get('number'), "qt_id": qt_id, "q_type": q.get('q_type'),
                  "q_attr": q.get('q_attr'),
                  "q_title": q.get('q_title'), "q_title_html": q.get('q_title_html'),
                  "q_check_role": q.get('q_check_role'),
                  "min_age": q.get('min_age'), 'max_age': q.get('max_age'), 'sex': q.get('sex')}
        if not q_id: # 新增时需要添加q_uid
            q_id = str(uuid.uuid4())
        cre = Question_tmp.objects.update_or_create(u_id=q_id, qt_id=qt_id, defaults=q_data)
        del_q_id.append(q_id)
        a_data_list = []
        del_a_id = [] # 删除使用
        for a in q.get('q_options', {}):
            a_id = q.get('o_id')
            if not a_id:
                a_id = str(uuid.uuid4())
            a_data = {"u_id": a_id, "q_id": q_id, "o_number": a.get('o_number'), "o_content": a.get('o_content'), "o_html_content": a.get('o_html_content')}
            an_cre = Option_tmp.objects.update_or_create(u_id=a_id, q_id=q_id, defaults=a_data)
            del_a_id.append(a_id)
            a_data_list.append({"u_id": a_id, "q_id": q_id, "o_number": a.get('o_number'),
                                 "o_content": a.get('o_content'), "o_html_content": a.get('o_html_content')})

        Option_tmp.objects.filter(~Q(u_id__in=del_a_id)).delete()  # 将多余的删除
        res.append({"q_id": q_id, "qt_id": qt_id, "number": q.get('number'), "q_type":q.get('q_type'),
                    "q_attr": q.get('q_attr'), "q_title": q.get('q_title'), "q_check_role": q.get('q_check_role'),
                    "options": a_data_list})
    Question_tmp.objects.filter(~Q(u_id__in=del_q_id)).delete()
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

def get_question_option(request):
    q_id = request.query_params.get("q_id")
    ops = Option_tmp.objects.filter(q_id=q_id)
    result = []
    for op in ops:
        result.append({"o_id": op.u_id, "o_number": op.o_number, "value": op.value})
    return result


def add_order_and_select_value(request):
    data = request.data
    values = data.get('values')
    for j in values:
        Option_tmp.objects.filter(q_id=j.get('q_id'), o_number=j.get('o_number')).update(value=j.get('value'))
    return

def add_calculate(request):
    data = request.data
    qt_id = data.get('qt_id')
    exp = data.get('exp')
    order = data.get('order')
    # 将以前录入的排序清空
    qs = Question_tmp.objects.filter(qt_id=qt_id)
    q_id_list = []
    for i in qs:
        q_id_list.append(i.u_id)
    Option_tmp.objects.filter(q_id__in=q_id_list).update(next_q_id="")
    # 置空后重新添加
    for i in order:
        Option_tmp.objects.filter(q_id=i.get('q_id'), o_number=i.get('o_number')).update(next_q_id=i.get('next_q_id'))
    #先将计算规则删除再添加
    Calculate_Exp_tmp.objects.filter(qt_id=qt_id).delete()
    for i in exp:
        i['qt_id'] = qt_id
        Calculate_Exp_tmp.objects.create(**i)
    return

def get_calculate(request):
    qt_id = request.query_params.get("qt_id")
    exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
    result = []
    for e in exps:
        ex = {"exp_id": e.u_id, "exp_name": e.exp_name, "exp_type": e.exp_type, "exp": e.exp}
        result.append(ex)
    return result

def add_result(request):
    data = request.data
    qt_id = data.get('qt_id')
    results = data.get('results')
    del_r_id_list = []
    for r in results:
        uid = r.get('r_id')
        if not uid:
            uid = str(uuid.uuid4())
        del_r_id_list.append(uid)
        res = {"u_id": uid, "qt_id": qt_id, "statement": r.get('statement', ''),
               "background_img": r.get('background_img',''), "result_img": r.get('result_img', '')}
        Result_Title_tmp.objects.update_or_create(u_id=uid, defaults=res)
        for dim in r.get('dimession', []):
            dimension_number = dim.get('dimension_number', '')
            dimension_name = dim.get('dimension_name', '')
            d_result = dim.get('d_result', [])
            del_dim_id_list = []
            for j in d_result:
                result_number = j.get('result_number', '')
                result_name = j.get('result_name', '')
                result_desc = j.get('result_desc', '')
                value = j.get('value', {})
                dim_u_id = j.get('dim_u_id')
                if not dim_u_id:
                    dim_u_id = str(uuid.uuid4())
                del_dim_id_list.append(dim_u_id)
                dim_data = {"u_id": dim_u_id, 'qt_id': qt_id, 'r_id': uid, "dimension_number": dimension_number,
                            "dimension_name": dimension_name, "result_number": result_number,
                            "result_name": result_name, "result_desc": result_desc, "value":value}
                Dimension_tmp.objects.update_or_create(u_id=dim_u_id, defaults=dim_data)
            Dimension_tmp.objects.filter(qt_id=qt_id, r_id=uid).filter(~Q(u_id__in=del_dim_id_list)).delete()
    Result_Title_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=del_r_id_list)).delete()
    return


def show_result(request):
    qt_id = request.query_params.get("qt_id")
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


def copy_tmp_table(qt_id):
    q = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    QuestionType.objects.update_or_create(u_id=qt_id, defaults={"background_img": q.background_img, 'title_img':q.title_img,
                        'title':q.title, 'test_value':q.test_value, 'test_value_html':q.test_value_html,
                        'q_number':q.q_number, 'test_time':q.test_time, 'use_count':q.use_count, 'source':q.source,
                        'status': q.status, 'status_tmp': q.status_tmp, 'show_number':q.show_number, 'finish_number': q.finish_number,
                        'update_user': q.update_user, 'create_user':q.create_user, 'check_user':q.check_user, 'start_time':q.start_time,
                        'end_time':q.end_time, 'create_time': q.create_time, 'update_time': q.update_time})
    qq = Question_tmp.objects.filter(qt_id=qt_id)
    q_uid_list = []
    for i in qq:
        q_uid_list.append(i.u_id)  # 记录更新的id,不在里面的需要删除
        Question.objects.update_or_create(qt_id=qt_id, u_id=i.u_id, defaults={'q_type':i.q_type,
                        'q_attr': i.q_attr, 'q_value_type':i.q_value_type, 'q_title': i.q_title,
                        'q_title_html':i.q_title_html, 'number':i.number, 'q_check_role':i.q_check_role,
                        "min_age": i.min_age,'max_age': i.max_age, 'sex': i.sex,
                        'create_time': i.create_time, 'update_time':i.update_time})
    Question.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=q_uid_list)).delete()

    ops = Option_tmp.objects.filter(q_id__in=q_uid_list)
    o_uid_list = []
    for j in ops:
        o_uid_list.append(j.u_id)
        Option.objects.update_or_create(q_id=j.q_id, u_id=j.u_id, defaults={
            'o_number':j.o_number, 'o_content':j.o_content, 'o_html_content':j.o_html_content,
            'next_q_id': j.next_q_id, 'value':j.value, 'create_time':j.create_time, 'update_time': j.update_time
        })
    Option.objects.filter(q_id__in=q_uid_list).filter(~Q(u_id__in=o_uid_list)).delete()

    cas = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
    ca_uid_list = []
    for m in cas:
        ca_uid_list.append(m.u_id)
        Calculate_Exp.objects.update_or_create(qt_id=qt_id, u_id=m.u_id, defaults={
            "exp_name": m.exp_name, 'exp_type':m.exp_type, 'exp': m.exp,
            'create_time': m.create_time, 'update_time':m.update_time
        })
    Calculate_Exp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=ca_uid_list)).delete()

    res = Result_Title_tmp.objects.filter(qt_id=qt_id)
    res_uid_list = []
    for r in res:
        res_uid_list.append(r.u_id)
        Result_Title.objects.update_or_create(qt_id=qt_id, u_id=r.u_id, defaults={
            'background_img': r.background_img, 'statement': r.statement,
            'result_img': r.result_img, 'create_time': r.create_time, 'update_time':r.update_time
        })
    Result_Title.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=res_uid_list))

    dim = Dimension_tmp.objects.filter(qt_id=qt_id, r_id__in=res_uid_list)
    dim_uid_list = []
    for d in dim:
        dim_uid_list.append(d.u_id)
        Dimension.objects.update_or_create(qt_id=qt_id, u_id=d.u_id, defaults={
            'r_id': d.r_id, 'dimension_number': d.dimension_number, 'dimension_name':d.dimension_name,
            'result_number': d.result_number, 'result_name': d.result_name, 'result_name_html':d.result_name_html,
            'result_desc': d.result_desc, 'result_desc_html': d.result_desc_html, 'value': d.value
        })
    Dimension.objects.filter(qt_id=qt_id, r_id__in=res_uid_list).filter(~Q(u_id__in=dim_uid_list)).delete()

    return




