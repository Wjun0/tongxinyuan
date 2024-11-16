import json
import re
import uuid

from django.db.models import Q

from apps.questions.check_data_service import check_start_end_time, check_img, check_add_question, check_add_calculate, \
    check_add_result
from apps.questions.models import Question, Option, Calculate_Exp, Question_tmp, Option_tmp, Calculate_Exp_tmp, \
    Result_Title, Result_Title_tmp, Dimension, Dimension_tmp, QuestionType_tmp, QuestionType, Channel_tmp, Channel, \
    ChannelData_tmp, ChannelData
from apps.users.exceptions import Exception_


def add_question_type(request):
    data = request.data
    background_img = data.get('background_img')
    title_img = data.get('title_img')
    title = data.get('title')
    test_value = data.get('test_value')
    qt_type = data.get('qt_type')
    q_number = data.get('q_number')
    test_time = data.get('test_time')
    use_count = data.get('use_count')
    source = data.get('source')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    amount = data.get('amount')
    pay_type = data.get('pay_type')
    if pay_type not in ['免费', '付费']:
        raise Exception_('问卷付费类型设置不正确！')
    if pay_type == "付费":
        try:
            amount = f'{float(amount):.2f}'
        except Exception as e:
            raise Exception_('问卷价格设置不正确！')
    # if not check_start_end_time(start_time, end_time):
    #     raise Exception_("时间格式错误！")
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
    if len(title) > 54:
        raise Exception_("问卷标题不超过54个字!")
    if qt_type not in ['文本', '语音/视频']:
        raise Exception_('类型不是文本|语音/视频')
    return True

def add_question(request):
    data = request.data
    qt_id = data.get("qt_id")
    questions = data.get('questions')
    res = []
    del_q_id = []  # 删除使用
    check_add_question(data)
    for q in questions:
        q_id = q.get('u_id')
        if not q_id: # 新增时需要添加q_uid
            q_id = str(uuid.uuid4())
        number = q.get('number')
        q_data = {"number": q.get('number'), "qt_id": qt_id, "u_id": q_id,
                  "q_attr": q.get('q_attr',''), "q_type": q.get('q_type', ''), 'qt_type':q.get('qt_type', ""),
                  "q_title": q.get('q_title', ''), "q_title_html": q.get('q_title_html', ''),
                  "q_check_role": q.get('q_check_role', ''),
                  "min_age": q.get('min_age', ''), 'max_age': q.get('max_age', ''), 'sex': q.get('sex', '')}
        cre = Question_tmp.objects.update_or_create(u_id=q_id, defaults=q_data)
        del_q_id.append(q_id)
        a_data_list = []
        del_a_id = [] # 删除使用
        for a in q.get('q_options', []):
            a_id = a.get('u_id')
            if not a_id:
                a_id = str(uuid.uuid4())
            a_data = {"u_id": a_id, "q_id": q_id, "o_number": a.get('o_number'), "o_content": a.get('o_content'), "o_html_content": a.get('o_html_content')}
            an_cre = Option_tmp.objects.update_or_create(u_id=a_id, defaults=a_data)
            del_a_id.append(a_id)
            a_data_list.append({"u_id": a_id, "q_id": q_id, "o_number": a.get('o_number'),
                                 "o_content": a.get('o_content'), "o_html_content": a.get('o_html_content')})

        Option_tmp.objects.filter(q_id=q_id).filter(~Q(u_id__in=del_a_id)).delete()  # 将多余的删除
        res.append({"q_id": q_id, "qt_id": qt_id, "number": q.get('number', ''), "q_type":q.get('q_type', ''),
                    "q_attr": q.get('q_attr', ''), "q_title": q.get('q_title', ''), "q_check_role": q.get('q_check_role', ''),
                    "q_options": a_data_list})
    Question_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=del_q_id)).delete()
    return res

def get_option_data(request):
    qt_id = request.query_params.get("qt_id")
    ques = Question_tmp.objects.filter(qt_id=qt_id)
    result = []
    for q in ques:
        ops = Option_tmp.objects.filter(q_id=q.u_id)
        ops_list = []
        for op in ops:
            ops_list.append({"o_number": op.o_number, "o_content": op.o_content, "value": op.value})
        result.append({"q_id": q.u_id, 'q_attr': q.q_attr, 'q_type': q.q_type, "number": q.number, "q_check_role": q.q_check_role, "q_options": ops_list})
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
    check_add_calculate(data)
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
        exp_id = i.get('exp_id', '')
        if not i.get('exp_id'):
            exp_id = str(uuid.uuid4())
        i['u_id'] = exp_id
        dic = {'u_id': exp_id, 'qt_id': qt_id, "exp_name": i.get('exp_name'), "exp_type": i.get('exp_type'),
                "formula": json.dumps(i.get('formula', [])), "exp": i.get('exp')}
        Calculate_Exp_tmp.objects.create(**dic)
    return

def get_calculate(request):
    qt_id = request.query_params.get("qt_id")
    exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
    exp = []
    for e in exps:
        ex = {"exp_id": e.u_id, "exp_name": e.exp_name, "exp_type": e.exp_type, "formula":json.loads(e.formula) ,"exp": e.exp}
        exp.append(ex)
    ques = Question_tmp.objects.filter(qt_id=qt_id)
    order = []
    for i in ques:
        q_id = i.u_id
        ans = Option_tmp.objects.filter(q_id=q_id)
        for j in ans:
            if j.next_q_id:
                # next = Option_tmp.objects.filter(q_id=j.next_q_id).first()
                order.append({"u_id": j.u_id, "q_id": q_id, "number": i.number, "o_number": j.o_number,
                              "o_content": j.o_content, "o_html_content": j.o_html_content, "next_q_id": j.next_q_id})
    return {"order": order, "exp": exp}

def add_result(request):
    data = request.data
    qt_id = data.get('qt_id')
    results = data.get('results', [])
    check_add_result(data)  # 数据校验
    del_r_id_list = []
    for r in results:
        uid = r.get('r_id')
        if not uid:
            uid = str(uuid.uuid4())
        del_r_id_list.append(uid)
        res = {"u_id": uid, "qt_id": qt_id, "statement": r.get('statement', ''),
               "background_img": r.get('background_img',''), "result_img": r.get('result_img', '')}
        Result_Title_tmp.objects.update_or_create(u_id=uid, qt_id=qt_id, defaults=res)

        for dim in r.get('dimension', []):
            dimension_number = dim.get('dimension_number', '')
            dimension_name = dim.get('dimension_name', '')
            d_result = dim.get('d_result', [])
            del_dim_res_num_list = []
            for j in d_result:
                result_number = j.get('result_number', '')
                result_name = j.get('result_name', '')
                result_name_html = j.get('result_name_html', '')
                result_desc = j.get('result_desc', '')
                result_desc_html = j.get('result_desc_html', '')
                value = j.get('value', {})
                dim_u_id = j.get('dim_u_id')
                if not dim_u_id:
                    dim_u_id = str(uuid.uuid4())
                del_dim_res_num_list.append(result_number)
                dim_data = {"u_id": dim_u_id, 'qt_id': qt_id, 'r_id': uid, "dimension_number": dimension_number,
                            "dimension_name": dimension_name, "result_number": result_number,
                            'result_name_html': result_name_html, 'result_desc_html':result_desc_html,
                            "result_name": result_name, "result_desc": result_desc, "value":value}
                Dimension_tmp.objects.update_or_create(qt_id=qt_id, dimension_number=dimension_number, result_number=result_number, defaults=dim_data)
            Dimension_tmp.objects.filter(qt_id=qt_id, dimension_number=dimension_number).\
                filter(~Q(result_number__in=del_dim_res_num_list)).delete()
    Result_Title_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=del_r_id_list)).delete()
    return

def get_add_result(request):
    qt_id = request.query_params.get("qt_id")
    result = []
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if qt:
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
            for m, v in dimension_dic.items():
                ds = Dimension_tmp.objects.filter(qt_id=qt_id, r_id=r_id, dimension_number=m)
                res_list = []
                for d in ds:
                    r_d = {"result_number": d.result_number, "result_name": d.result_name,
                           'result_name_html': d.result_name_html,
                           "result_desc": d.result_desc, "result_desc_html": d.result_desc_html, "value": d.value}
                    res_list.append(r_d)
                s = {"dimension_number": m, "dimension_name": v, "d_result": res_list}
                dimensions.append(s)
            dim_tp = {"background_img": background_img, "statement": statement, "dimensions": dimensions,
                      "result_img": result_img}
            result.append(dim_tp)
    return result


def show_result(request):
    qt_id = request.query_params.get("qt_id")
    result = {}
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if qt:
        step1 = {"qt_id": qt.u_id, "start_time": qt.start_time, "end_time": qt.end_time, "background_img": qt.background_img, 'title_img': qt.title_img,
             "title":qt.title, "test_value": qt.test_value, "q_number": qt.q_number, "test_time": qt.test_time, "qt_type": qt.qt_type,
             "use_count": qt.use_count, "source": qt.source, "pay_type": qt.pay_type, "amount": qt.amount}
        result["step1"] = step1
        ques = Question_tmp.objects.filter(qt_id=qt_id)
        questions = []
        order = []
        for i in ques:
            q_id = i.u_id
            ans = Option_tmp.objects.filter(q_id=q_id)
            options = []
            for j in ans:
                options.append({"u_id": j.u_id, "q_id": q_id, "o_number": j.o_number, "o_content": j.o_content,
                                "o_html_content": j.o_html_content, "next_q_id": j.next_q_id, "value":j.value})
                if j.next_q_id:
                    # next = Option_tmp.objects.filter(q_id=j.next_q_id).first()
                    order.append({"u_id": j.u_id, "q_id": q_id, "number": i.number, "o_number": j.o_number,
                                  "o_content": j.o_content, "o_html_content": j.o_html_content,
                                  "next_q_id": j.next_q_id})
            questions.append({"u_id": i.u_id, "qt_id": i.qt_id, "q_type": i.q_type, 'q_attr':i.q_attr, 'q_value_type':i.q_value_type,
                              "q_title": i.q_title, "q_title_html":i.q_title_html ,"number": i.number, "q_check_role": i.q_check_role,
                              "min_age":i.min_age,"max_age": i.max_age,"sex":i.sex, "q_options": options})
        result["step2"] = questions
        exp_list = []
        exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
        for m in exps:
            exp_list.append({"exp_name": m.exp_name, "exp": m.exp, "exp_type": m.exp_type, "formula":m.formula})
        result['step3'] = {"order": order, "exp": exp_list}

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
            for m, v in dimension_dic.items():
                ds = Dimension_tmp.objects.filter(qt_id=qt_id, r_id=r_id, dimension_number=m)
                res_list = []
                for d in ds:
                    r_d = {"result_number": d.result_number, "result_name": d.result_name, 'result_name_html':d.result_name_html,
                           "result_desc": d.result_desc,"result_desc_html": d.result_desc_html, "value": d.value}
                    res_list.append(r_d)
                s = {"dimension_number": m, "dimension_name":v, "d_result": res_list}
                dimensions.append(s)
            dim_tp = {"background_img":background_img, "statement":statement, "dimensions": dimensions, "result_img": result_img}
            step4.append(dim_tp)
        result["step4"] = step4
    return result


def copy_tmp_table(qt_id):
    q = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    QuestionType.objects.update_or_create(u_id=qt_id, defaults={"background_img": q.background_img, 'title_img':q.title_img,
                        'title':q.title, 'test_value':q.test_value, 'test_value_html':q.test_value_html,
                        'q_number':q.q_number, 'test_time':q.test_time, 'use_count':q.use_count, 'source':q.source,
                        'status': q.status, 'status_tmp': q.status_tmp, 'show_number':q.show_number, 'finish_number': q.finish_number,
                        'update_user': q.update_user, 'create_user':q.create_user, 'check_user':q.check_user,
                        "amount": q.amount, "pay_type": q.pay_type, 'check_time':q.check_time,
                        'start_time':q.start_time, 'end_time':q.end_time, 'create_time': q.create_time, 'update_time': q.update_time})
    qq = Question_tmp.objects.filter(qt_id=qt_id)
    q_uid_list = []
    for i in qq:
        q_uid_list.append(i.u_id)  # 记录更新的id,不在里面的需要删除
        Question.objects.update_or_create(qt_id=qt_id, number=i.number,
                                          defaults={'u_id':i.u_id, 'q_type':i.q_type,
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
            "exp_name": m.exp_name, 'exp_type':m.exp_type, 'exp': m.exp, 'formula': m.formula,
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
    Result_Title.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=res_uid_list)).delete()

    dim = Dimension_tmp.objects.filter(qt_id=qt_id, r_id__in=res_uid_list)
    dim_uid_list = []
    for d in dim:
        dim_uid_list.append(d.u_id)
        Dimension.objects.update_or_create(qt_id=qt_id, u_id=d.u_id, defaults={
            'r_id': d.r_id, 'dimension_number': d.dimension_number, 'dimension_name':d.dimension_name,
            'result_number': d.result_number, 'result_name': d.result_name, 'result_name_html':d.result_name_html,
            'result_desc': d.result_desc, 'result_desc_html': d.result_desc_html, 'value': d.value
        })
    Dimension.objects.filter(qt_id=qt_id).filter(~Q(r_id__in=res_uid_list)).delete()
    Dimension.objects.filter(qt_id=qt_id, r_id__in=res_uid_list).filter(~Q(u_id__in=dim_uid_list)).delete()

    return


def copy_use_table(qt_id):
    q = QuestionType.objects.filter(u_id=qt_id).first()
    QuestionType_tmp.objects.update_or_create(u_id=qt_id, defaults={"background_img": q.background_img, 'title_img':q.title_img,
                        'title':q.title, 'test_value':q.test_value, 'test_value_html':q.test_value_html,
                        'q_number':q.q_number, 'test_time':q.test_time, 'use_count':q.use_count, 'source':q.source,
                        'status': q.status, 'status_tmp': q.status_tmp, 'show_number':q.show_number, 'finish_number': q.finish_number,
                        'update_user': q.update_user, 'create_user':q.create_user, 'check_user':q.check_user, 'start_time':q.start_time,
                        'end_time':q.end_time, 'create_time': q.create_time, 'update_time': q.update_time})
    qq = Question.objects.filter(qt_id=qt_id)
    q_uid_list = []
    for i in qq:
        q_uid_list.append(i.u_id)  # 记录更新的id,不在里面的需要删除
        Question_tmp.objects.update_or_create(qt_id=qt_id, u_id=i.u_id, defaults={'q_type':i.q_type,
                        'q_attr': i.q_attr, 'q_value_type':i.q_value_type, 'q_title': i.q_title,
                        'q_title_html':i.q_title_html, 'number':i.number, 'q_check_role':i.q_check_role,
                        "min_age": i.min_age,'max_age': i.max_age, 'sex': i.sex,
                        'create_time': i.create_time, 'update_time':i.update_time})
    Question_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=q_uid_list)).delete()

    ops = Option.objects.filter(q_id__in=q_uid_list)
    o_uid_list = []
    for j in ops:
        o_uid_list.append(j.u_id)
        Option_tmp.objects.update_or_create(q_id=j.q_id, u_id=j.u_id, defaults={
            'o_number':j.o_number, 'o_content':j.o_content, 'o_html_content':j.o_html_content,
            'next_q_id': j.next_q_id, 'value':j.value, 'create_time':j.create_time, 'update_time': j.update_time
        })
    Option_tmp.objects.filter(q_id__in=q_uid_list).filter(~Q(u_id__in=o_uid_list)).delete()

    cas = Calculate_Exp.objects.filter(qt_id=qt_id)
    ca_uid_list = []
    for m in cas:
        ca_uid_list.append(m.u_id)
        Calculate_Exp_tmp.objects.update_or_create(qt_id=qt_id, u_id=m.u_id, defaults={
            "exp_name": m.exp_name, 'exp_type':m.exp_type, 'exp': m.exp, 'formula': m.formula,
            'create_time': m.create_time, 'update_time':m.update_time
        })
    Calculate_Exp_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=ca_uid_list)).delete()

    res = Result_Title.objects.filter(qt_id=qt_id)
    res_uid_list = []
    for r in res:
        res_uid_list.append(r.u_id)
        Result_Title_tmp.objects.update_or_create(qt_id=qt_id, u_id=r.u_id, defaults={
            'background_img': r.background_img, 'statement': r.statement,
            'result_img': r.result_img, 'create_time': r.create_time, 'update_time':r.update_time
        })
    Result_Title_tmp.objects.filter(qt_id=qt_id).filter(~Q(u_id__in=res_uid_list))

    dim = Dimension.objects.filter(qt_id=qt_id, r_id__in=res_uid_list)
    dim_uid_list = []
    for d in dim:
        dim_uid_list.append(d.u_id)
        Dimension_tmp.objects.update_or_create(qt_id=qt_id, u_id=d.u_id, defaults={
            'r_id': d.r_id, 'dimension_number': d.dimension_number, 'dimension_name':d.dimension_name,
            'result_number': d.result_number, 'result_name': d.result_name, 'result_name_html':d.result_name_html,
            'result_desc': d.result_desc, 'result_desc_html': d.result_desc_html, 'value': d.value
        })
    Dimension_tmp.objects.filter(qt_id=qt_id, r_id__in=res_uid_list).filter(~Q(u_id__in=dim_uid_list)).delete()

    return

def copy_used_channel_table(type):
    c = Channel.objects.filter(type=type).first()
    if c:
        data = {}
        data['u_id'] = c.u_id
        data['main_title'] = c.main_title
        data['type'] = c.type
        data['update_user'] = c.update_user
        data['create_user'] = c.create_user
        data['check_user'] = c.check_user
        data['status'] = c.status
        data['create_time'] = c.create_time
        data['update_time'] = c.update_time
        Channel_tmp.objects.update_or_create(type=type, defaults=data)
        cds = ChannelData.objects.filter(type=type)
        index_list = []
        for i in cds:
            item = {}
            item['u_id'] = i.u_id
            item['index'] = i.index
            item['qt_id'] = i.qt_id
            item['source'] = i.source
            item['title'] = i.title
            item['img'] = i.img
            item['url'] = i.url
            item['type'] = i.type
            item['desc'] = i.desc
            item['amount'] = i.amount
            item['pay_type'] = i.pay_type
            item['create_time'] = i.create_time
            item['update_time'] = i.update_time
            item['status'] = i.status
            index_list.append(i.index)
            ChannelData_tmp.objects.update_or_create(type=type, index=i.index, defaults=item)
        ChannelData_tmp.objects.filter(type=type).filter(~Q(index__in=index_list)).delete()


def copy_question(qt_id, user):
    q = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if q:
        new_qt_id = str(uuid.uuid4())
        title = "【复制】" + q.title
        QuestionType_tmp.objects.create(u_id=new_qt_id, background_img=q.background_img, title_img=q.title_img, title=title,
            test_value=q.test_value, test_value_html=q.test_value_html, q_number=q.q_number, qt_type=q.qt_type,
            test_time=q.test_time, use_count=q.use_count, source=q.source, status="草稿", status_tmp="草稿",
            show_number=0, finish_number=0, update_user=user, create_user=user, check_user='',
            amount=q.amount, pay_type=q.pay_type, start_time=q.start_time, end_time=q.end_time)
        ques = Question_tmp.objects.filter(qt_id=qt_id)
        old_new_dic = {}
        for i in ques:
            new_q_id = str(uuid.uuid4())
            Question_tmp.objects.create(u_id=new_q_id, qt_id=new_qt_id, q_type=i.q_type, qt_type=i.qt_type, q_attr=i.q_attr,
                        q_value_type=i.q_value_type, q_title=i.q_title, q_title_html=i.q_title_html,
                        number=i.number, q_check_role=i.q_check_role, min_age=i.min_age, max_age=i.max_age,
                        sex=i.sex)
            ops = Option_tmp.objects.filter(q_id=i.u_id)
            old_new_dic[i.u_id] = new_q_id
            for op in ops:
                o_u_id = str(uuid.uuid4())
                Option_tmp.objects.create(u_id=o_u_id, q_id=new_q_id, o_number=op.o_number, o_content=op.o_content,
                        o_html_content=op.o_html_content, next_q_id='', value=op.value)
        for j in ques:
            ops = Option_tmp.objects.filter(q_id=j.u_id)
            for k in ops:
                if k.next_q_id:
                    new_q_id = old_new_dic.get(k.u_id)
                    new_next_q_id = old_new_dic.get(k.next_q_id)
                    Option_tmp.objects.filter(u_id=new_q_id).update(next_q_id=new_next_q_id)

        old_exp_dic = {}
        exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
        for e in exps:
            new_exp_id = str(uuid.uuid4())
            formula = e.formula
            par = re.compile(r'{.*?}', )
            exp_str = e.exp
            res = par.findall(e.exp)
            for r in res:  # 将所有的变量都替换为值
                key = r.replace('{', '').replace('}', '')
                v = old_new_dic.get(key, '')
                exp_str = exp_str.replace(key, v)
            new_formula = []
            for f in eval(formula):
                if f.get('type') == "question_id":
                    value = f.get('value')
                    new_value = old_new_dic.get(value, '')
                    f['value'] = new_value
                new_formula.append(f)
            Calculate_Exp_tmp.objects.create(u_id=new_exp_id, qt_id=new_qt_id, exp_name=e.exp_name,
                                            exp_type=e.exp_type, exp=exp_str, formula=json.dumps(new_formula),
                                            create_time=e.create_time, update_time=e.update_time)
            old_exp_dic[e.u_id] = new_exp_id

        old_rt_id_dic = {}
        rts = Result_Title_tmp.objects.filter(qt_id=qt_id)
        for rt in rts:
            r_id = str(uuid.uuid4())
            Result_Title_tmp.objects.create(u_id=r_id, qt_id=new_qt_id, background_img=rt.background_img,
                                            statement=rt.statement, result_img=rt.result_img,
                                            create_time=rt.create_time, update_time=rt.update_time)
            old_rt_id_dic[rt.u_id] = r_id

        dims = Dimension_tmp.objects.filter(qt_id=qt_id)
        for d in dims:
            d_id = str(uuid.uuid4())
            new_r_id = old_rt_id_dic.get(d.r_id, '')
            value = d.value
            factor_list = value.get('factor_list', [])
            new_factor_list = []
            for i in factor_list:
                exp_id = i.get('exp_id')
                new_exp_id = old_exp_dic.get(exp_id)
                i['exp_id'] = new_exp_id
                new_factor_list.append(i)
            new_value = {}
            new_value['value'] = value.get('value', '')
            new_value['numKeys'] = value.get('numKeys', '')
            new_value['condition'] = value.get('condition', '')
            new_value['factor_list'] = new_factor_list
            Dimension_tmp.objects.create(u_id=d_id, qt_id=new_qt_id, r_id=new_r_id, dimension_number=d.dimension_number,
                                         dimension_name=d.dimension_name, result_number=d.result_number,
                                         result_name=d.result_name, result_name_html=d.result_name_html,
                                         result_desc=d.result_desc, result_desc_html=d.result_desc_html, value=new_value)
        return new_qt_id, title
    return None

def copy_channel_tmp_table(type):
    c = Channel_tmp.objects.filter(type=type).first()
    if c:
        data = {}
        data['u_id'] = c.u_id
        data['main_title'] = c.main_title
        data['type'] = c.type
        data['update_user'] = c.update_user
        data['create_user'] = c.create_user
        data['check_user'] = c.check_user
        data['status'] = c.status
        data['create_time'] = c.create_time
        data['update_time'] = c.update_time
        Channel.objects.update_or_create(type=type, defaults=data)
        cds = ChannelData_tmp.objects.filter(type=type)
        index_list = []
        for i in cds:
            item = {}
            item['u_id'] = i.u_id
            item['index'] = i.index
            item['qt_id'] = i.qt_id
            item['source'] = i.source
            item['title'] = i.title
            item['img'] = i.img
            item['url'] = i.url
            item['type'] = i.type
            item['desc'] = i.desc
            item['amount'] = i.amount
            item['pay_type'] = i.pay_type
            item['create_time'] = i.create_time
            item['update_time'] = i.update_time
            item['status'] = i.status
            index_list.append(i.index)
            ChannelData.objects.update_or_create(type=type, index=i.index, defaults=item)
        ChannelData.objects.filter(type=type).filter(~Q(index__in=index_list)).delete()
    return

def check_channel_add_data(data):
    main_title = data.get('main_title', '')
    type = data.get('type')
    channels = data.get('channel', [])
    if type not in ['banner', '金刚位', '横滑列表', '纵向列表']:
        raise Exception_(f'不支持{type}频道类型')
    if len(main_title) > 10:
        raise Exception_("主标题不能超过10个字！")
    if type=="banner" and len(channels) > 10:
        raise Exception_('banner 类型最多只能配置10条数据！')
    if type == "金刚位" and len(channels) > 4:
        raise Exception_('金刚位最多只能配置4条数据！')
    if type == "横滑列表" and len(channels) > 50:
        raise Exception_('横滑列表最多只能配置50条数据！')
    if type == "纵向列表" and len(channels) > 100:
        raise Exception_('纵向列表最多只能配置100条数据！')
    index = 1
    for i in channels:
        if int(i.get('index', '0')) != index:
            raise Exception_(f'编号index {i.index}错误！')
        index += 1
    return

