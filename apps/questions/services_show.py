from apps.questions.models import QuestionType_tmp, Question_tmp, Option_tmp, Calculate_Exp_tmp, Result_Title_tmp, \
    Dimension_tmp, QuestionType, Question, Option, Calculate_Exp, Result_Title, Dimension


def get_show_question(qt_id):
    result_tmp = {}
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if qt:
        step1 = {"qt_id": qt.u_id, "start_time": qt.start_time, "end_time": qt.end_time, "background_img": qt.background_img, 'title_img': qt.title_img,
             "title":qt.title, "test_value": qt.test_value, "q_number": qt.q_number, "test_time": qt.test_time, "pay_type":qt.pay_type, 'amount':qt.amount,
             "use_count": qt.use_count, "source": qt.source}
        result_tmp["step1"] = step1
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
                              "min_age":i.min_age,"max_age": i.max_age, "sex":i.sex, "q_options": options})
        result_tmp["step2"] = questions
        exp_list = []
        exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id)
        for m in exps:
            exp_list.append({"exp_name": m.exp_name, "exp": m.exp, "exp_type": m.exp_type, "formula":m.formula})
        result_tmp['step3'] = {"order": order, "exp": exp_list}

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
        result_tmp["step4"] = step4

    ###############################
    result = {}
    qt = QuestionType.objects.filter(u_id=qt_id).first()
    if qt:
        step1 = {"qt_id": qt.u_id, "start_time": qt.start_time, "end_time": qt.end_time,
                 "background_img": qt.background_img, 'title_img': qt.title_img,
                 "title": qt.title, "test_value": qt.test_value, "q_number": qt.q_number, "test_time": qt.test_time,
                 "use_count": qt.use_count, "source": qt.source}
        result["step1"] = step1
        ques = Question.objects.filter(qt_id=qt_id)
        questions = []
        order = []
        for i in ques:
            q_id = i.u_id
            ans = Option.objects.filter(q_id=q_id)
            options = []
            for j in ans:
                options.append({"u_id": j.u_id, "q_id": q_id, "o_number": j.o_number, "o_content": j.o_content,
                                "o_html_content": j.o_html_content, "next_q_id": j.next_q_id, "value": j.value})
                if j.next_q_id:
                    # next = Option_tmp.objects.filter(q_id=j.next_q_id).first()
                    order.append({"u_id": j.u_id, "q_id": q_id, "number": i.number, "o_number": j.o_number,
                                  "o_content": j.o_content, "o_html_content": j.o_html_content,
                                  "next_q_id": j.next_q_id})
            questions.append({"u_id": i.u_id, "qt_id": i.qt_id, "q_type": i.q_type, 'q_attr': i.q_attr,
                              'q_value_type': i.q_value_type,
                              "q_title": i.q_title, "q_title_html": i.q_title_html, "number": i.number,
                              "q_check_role": i.q_check_role,
                              "min_age": i.min_age, "max_age": i.max_age, "sex": i.sex, "q_options": options})
        result["step2"] = questions
        exp_list = []
        exps = Calculate_Exp.objects.filter(qt_id=qt_id)
        for m in exps:
            exp_list.append({"exp_name": m.exp_name, "exp": m.exp, "exp_type": m.exp_type, "formula": m.formula})
        result['step3'] = {"order": order, "exp": exp_list}

        step4 = []
        res = Result_Title.objects.filter(qt_id=qt_id)
        for i in res:
            r_id = i.u_id
            background_img = i.background_img
            statement = i.statement
            result_img = i.result_img
            dims = Dimension.objects.filter(qt_id=qt_id, r_id=r_id)
            dimension_dic = {}
            for j in dims:
                dimension_dic[j.dimension_number] = j.dimension_name
            dimensions = []
            for m, v in dimension_dic.items():
                ds = Dimension.objects.filter(qt_id=qt_id, r_id=r_id, dimension_number=m)
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
            step4.append(dim_tp)
        result["step4"] = step4

    return {"data_tmp": result_tmp, "data": result}


def get_used_question(keyword):
    if keyword:
        ques = QuestionType.objects.filter(status="已上线").filter(title__icontains=keyword)
    else:
        ques = QuestionType.objects.filter(status="已上线")
    data = []
    for i in ques:
        item = {}
        item['qt_id'] = i.u_id
        item['title'] = i.title
        data.append(item)
    return data

