import logging
import re

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from apps.questions.models import Dimension, Question, Option, Calculate_Exp, Result_Title, QuestionType, \
    QuestionType_tmp, Option_tmp, Question_tmp, Dimension_tmp, Calculate_Exp_tmp, Result_Title_tmp
from apps.users.exceptions import Exception_
from apps.users.utils import get_user_id
from apps.wechats.models import UserAnswer, UserShow_number, UserAnswer_tmp, Order, Order_tmp

format_dic = {"大于": ">", "大于或等于": ">=",
              "小于": "<", "小于或等于": "<=",
              "等于": "=", "不等于": "!="}

def check_age(qt_id, min_age_max_age, answer):
    q = Question.objects.filter(qt_id=qt_id, q_attr="年龄题").first()
    if not q: # 没有配置年龄题目
        return False
    user_o_number = answer.get(q.u_id, {}).get("o_number")
    op = Option.objects.filter(q_id=q.u_id, o_number=user_o_number).first() # 找到用户选择的选项
    if not op:
        return False
    if op.o_content == min_age_max_age:
        # 用户选项的年龄字符串和结果配置的字符串相同
        return True
    return False

def check_sex(qt_id, sex, answer):
    q = Question.objects.filter(qt_id=qt_id, q_attr="性别题").first()
    if not q:  # 没有配置年龄题目
        return False
    user_o_number = answer.get(q.u_id, {}).get("o_number")
    op = Option.objects.filter(q_id=q.u_id, o_number=user_o_number).first()  # 找到用户选择的性别
    if not op:
        return False
    if op.o_content == sex:
        return True  # 用户选择的和结果校验配置的相同才通过
    return False

def generate_user_answer_data(answer):
    # 生成用户选择的数据结果
    result = {}
    count_result_list = []
    for q_id,v in answer.items():
        # 需要将性别题和年龄题去掉
        q = Question.objects.filter(u_id=q_id).first()
        if not q:
            continue
        if q.q_attr in ['性别题', '年龄题']:
            count_result_list.append({"number": q.number, "q_attr": q.q_attr, "o_number": v.get('o_number', '')})
            continue
        o_number = v.get('o_number')
        if ',' in o_number: # 多选题
            o_number_list = o_number.split(',')
            for i in o_number_list:
                obj = Option.objects.filter(q_id=q_id, o_number=i).first()
                if obj:
                    value = obj.value
                    try:
                        int(value)  # 数值计算
                        d = result.get(value, 0)  # 多选的结果相加
                        result[q_id] = int(d) + int(value)
                        count_result_list.append({"number": q.number, "q_attr": q.q_attr ,"o_number": i, "value": d})
                    except Exception as e:  # 统计计算
                        # 查询是否有值
                        count_result_list.append({"number": q.number, "q_attr": q.q_attr ,"o_number": i, "value": value})
                        d = result.get(value, 0)
                        result[value] = d + 1
        else: # 单选题
            obj = Option.objects.filter(q_id=q_id, o_number=o_number).first()
            if obj:
                value = obj.value
                count_result_list.append(
                    {"number": q.number, "q_attr": q.q_attr, "o_number": obj.o_number, "value": value})
                try:
                    int(value)  # 数值计算
                    result[q_id] = int(value)
                except Exception as e: # 统计计算
                    # 查询是否有值
                    d = result.get(value, 0)
                    result[value] = d +1

    return result, count_result_list

def generate_user_answer_tmp_data(answer):
    # 生成用户选择的数据结果
    result = {}
    for q_id,v in answer.items():
        # 需要将性别题和年龄题去掉
        q = Question_tmp.objects.filter(u_id=q_id).first()
        if not q:
            continue
        if q.q_attr in ['性别题', '年龄题']:
            continue
        o_number = v.get('o_number')
        if ',' in o_number: # 多选题
            o_number_list = o_number.split(',')
            for i in o_number_list:
                obj = Option_tmp.objects.filter(q_id=q_id, o_number=i).first()
                if obj:
                    value = obj.value
                    try:
                        int(value)  # 数值计算
                        d = result.get(value, 0)  # 多选的结果相加
                        result[q_id] = int(d) + int(value)
                    except Exception as e:  # 统计计算
                        # 查询是否有值
                        d = result.get(value, 0)
                        result[value] = d + 1
        else: # 单选题
            obj = Option_tmp.objects.filter(q_id=q_id, o_number=o_number).first()
            if obj:
                value = obj.value
                try:
                    int(value)  # 数值计算
                    result[q_id] = int(value)
                except Exception as e: # 统计计算
                    # 查询是否有值
                    d = result.get(value, 0)
                    result[value] = d +1
    return result


def generate_result(qt_id, ans_id):
    ans_obj = UserAnswer.objects.filter(u_id=ans_id, qt_id=qt_id).first()
    if not ans_obj:
        raise Exception_("找不到问卷结果！")
    if ans_obj.result: # 已经生成结果直接返回
        return
    answer = ans_obj.answer
    qt = QuestionType.objects.filter(u_id=qt_id).first()
    if qt.qt_type == "语音/视频":
        r_u_id = ''
        background_img = ''
        statement = ''
        result_img = ''
        dim_list = []
        title_img = ''
        dim_data = {"dimension_number": "", "dimension_name": "",
                    "result_number": "", "result_name": "",
                    "result_name_html": "", "result_desc": "问卷提交成功",
                    "result_desc_html": '[{\"type\": \"string\", \"value\": \"问卷提交成功\"}]', "value": ""}
        dim_list.append(dim_data)
        res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img": background_img, "statement": statement,
               "result_img": result_img, "dim_list": dim_list, "title_img": title_img}
        ans_obj.result = res
        ans_obj.save()
        return
    try:
        ans_data, count_result_list = generate_user_answer_data(answer)
        ans_obj.count_result = {"option_data": count_result_list, "ans_data": ans_data}
        tmp_dim_list = []  # 用户维度去重
        dim_id_list = []   # 用于存放结果
        dims = Dimension.objects.filter(qt_id=qt_id)
        for i in dims:
            # 该维度已经有结果就跳过
            if i.dimension_number not in tmp_dim_list:
                value = i.value
                if value.get('condition') =="年龄校验":
                    min_age_max_age = value.get('value')
                    if not check_age(qt_id, min_age_max_age, answer): # 校验不通过
                        continue
                elif value.get('condition') =="性别校验":
                    sex = value.get('value')
                    if not check_sex(qt_id, sex, answer): # 校验不通过
                        continue # 结束对该结果判断
                # 正常判断逻辑
                factor_list = value.get("factor_list")
                calculate = "" # 替换数据后的计算公式  示例："4>3 and 5>4"
                for j in factor_list:
                    exp_id = j.get('exp_id')
                    format = j.get('format')
                    value = j.get('value')
                    link = j.get('link')
                    # 根据exp_id 获取exp表达式
                    exp_obj = Calculate_Exp.objects.filter(u_id=exp_id).first()
                    if not exp_obj: # 找不到就跳过
                        continue
                    par = re.compile(r'{.*?}', )
                    exp_str = exp_obj.exp
                    res = par.findall(exp_obj.exp)
                    for r in res: # 将所有的变量都替换为值
                        key = r.replace('{','').replace('}','')
                        v = ans_data.get(key, 0)
                        new_exp_str = exp_str.replace(str(r), str(v))  # 将表达式中的变量替换为对应的值
                        exp_str = new_exp_str
                    exp_v = eval(exp_str)  # 得到因子的值
                    add_cal = str(exp_v) + str(format_dic.get(format)) + str(value)
                    if link:
                        add_cal = add_cal + link
                    calculate = calculate + add_cal

                calculate = calculate.replace("且", " and ").replace("或", " or ")
                dim_res = eval(calculate)
                if dim_res: # 条件成立
                    tmp_dim_list.append(i.dimension_number)
                    dim_id_list.append(i.u_id)
        # 将结果保存到 UserAnswer result
        r_u_id = ''
        background_img = ''
        statement = ''
        result_img = ''
        dim_list = []
        title_img = ''
        if not dim_id_list:
            # 一个维度都没有匹配上手动异常，获取默认结果
            logger = logging.getLogger("log")
            logger.error('=====没有匹配的结果======')
            raise Exception
        for u_id in dim_id_list:
            d = Dimension.objects.filter(u_id=u_id).first()
            if d:
                dim_data = {"dimension_number": d.dimension_number, "dimension_name": d.dimension_name,
                            "result_number": d.result_number, "result_name":d.result_name,
                            "result_name_html":d.result_name_html, "result_desc": d.result_desc,
                            "result_desc_html": d.result_desc_html, "value": d.value}
                dim_list.append(dim_data)
                obj = Result_Title.objects.filter(u_id=d.r_id).first()
                if obj:
                    r_u_id = obj.u_id
                    qt_id = obj.qt_id
                    background_img = obj.background_img
                    statement = obj.statement
                    result_img = obj.result_img
        if background_img:
            background_img = settings.DOMAIN + "/media/image/" + background_img
        if result_img:
            result_img = settings.DOMAIN + "/media/image/" + result_img
        if qt.title_img:
            title_img = settings.DOMAIN + "/media/image/" + qt.title_img
        res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img":background_img, "statement":statement,
               "result_img": result_img, "dim_list": dim_list, "title_img": title_img}
    except Exception as e: # 异常就取第一个结果
        logger = logging.getLogger("log")
        logger.error('=====获取结果异常======')
        logger.error(e)
        r_u_id = ''
        background_img = ''
        statement = ''
        result_img = ''
        dim_list = []
        title_img = ''
        dim_data = {"dimension_number": "", "dimension_name": "",
                    "result_number": "", "result_name": "",
                    "result_name_html": "", "result_desc": "暂未获取到结果，请重新测试",
                    "result_desc_html": '[{\"type\": \"string\", \"value\": \"暂未获取到结果，请重新测试\"}]', "value": ""}
        dim_list.append(dim_data)
        res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img":background_img, "statement":statement,
               "result_img": result_img, "dim_list": dim_list, "title_img": title_img}
    ans_obj.result = res
    ans_obj.save()
    return

def generate_tmp_result(qt_id, ans_id):
    ans_obj = UserAnswer_tmp.objects.filter(u_id=ans_id, qt_id=qt_id).first()
    if not ans_obj:
        raise Exception_("找不到问卷结果！")
    if ans_obj.result: # 已经生成结果直接返回
        return
    answer = ans_obj.answer
    qt = QuestionType.objects.filter(u_id=qt_id).first()
    try:
        ans_data = generate_user_answer_tmp_data(answer)
        tmp_dim_list = []  # 用户维度去重
        dim_id_list = []   # 用于存放结果
        dims = Dimension_tmp.objects.filter(qt_id=qt_id)
        for i in dims:
            # 该维度已经有结果就跳过
            if i.dimension_number not in tmp_dim_list:
                value = i.value
                if value.get('condition') =="年龄校验":
                    min_age_max_age = value.get('value')
                    if not check_age(qt_id, min_age_max_age, answer): # 校验不通过
                        continue
                elif value.get('condition') =="性别校验":
                    sex = value.get('value')
                    if not check_sex(qt_id, sex, answer): # 校验不通过
                        continue # 结束对该结果判断
                # 正常判断逻辑
                factor_list = value.get("factor_list")
                calculate = "" # 替换数据后的计算公式  示例："4>3 and 5>4"
                for j in factor_list:
                    exp_id = j.get('exp_id')
                    format = j.get('format')
                    value = j.get('value')
                    link = j.get('link')
                    # 根据exp_id 获取exp表达式
                    exp_obj = Calculate_Exp_tmp.objects.filter(u_id=exp_id).first()
                    if not exp_obj: # 找不到就跳过
                        continue
                    par = re.compile(r'{.*?}', )
                    exp_str = exp_obj.exp
                    res = par.findall(exp_obj.exp)
                    for r in res: # 将所有的变量都替换为值
                        key = r.replace('{','').replace('}','')
                        v = ans_data.get(key, 0)
                        new_exp_str = exp_str.replace(str(r), str(v))  # 将表达式中的变量替换为对应的值
                        exp_str = new_exp_str
                    exp_v = eval(exp_str)  # 得到因子的值
                    add_cal = str(exp_v) + str(format_dic.get(format)) + str(value)
                    if link:
                        add_cal = add_cal + link
                    calculate = calculate + add_cal

                calculate = calculate.replace("且", " and ").replace("或", " or ")
                dim_res = eval(calculate)
                if dim_res: # 条件成立
                    tmp_dim_list.append(i.dimension_number)
                    dim_id_list.append(i.u_id)
        # 将结果保存到 UserAnswer result
        r_u_id = ''
        qt_id = ''
        background_img = ''
        statement = ''
        result_img = ''
        dim_list = []
        title_img = ''
        if not dim_id_list:
            # 一个维度都没有匹配上手动异常，获取默认结果
            logger = logging.getLogger("log")
            logger.error('=====没有匹配的结果======')
            raise Exception
        for u_id in dim_id_list:
            d = Dimension_tmp.objects.filter(u_id=u_id).first()
            if d:
                dim_data = {"dimension_number": d.dimension_number, "dimension_name": d.dimension_name,
                            "result_number": d.result_number, "result_name":d.result_name,
                            "result_name_html":d.result_name_html, "result_desc": d.result_desc,
                            "result_desc_html": d.result_desc_html, "value": d.value}
                dim_list.append(dim_data)
                obj = Result_Title_tmp.objects.filter(u_id=d.r_id).first()
                if obj:
                    r_u_id = obj.u_id
                    qt_id = obj.qt_id
                    background_img = obj.background_img
                    statement = obj.statement
                    result_img = obj.result_img
        if background_img:
            background_img = settings.DOMAIN + "/media/image/" + background_img
        if result_img:
            result_img = settings.DOMAIN + "/media/image/" + result_img
        if qt.title_img:
            title_img = settings.DOMAIN + "/media/image/" + qt.title_img
        res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img":background_img, "statement":statement,
               "result_img": result_img, "dim_list": dim_list, "title_img": title_img}
    except Exception as e: # 异常就取第一个结果
        logger = logging.getLogger("log")
        logger.error('=====获取结果异常======')
        logger.error(e)
        r_u_id = ''
        background_img = ''
        statement = ''
        result_img = ''
        dim_list = []
        title_img = ''
        dim_data = {"dimension_number": "", "dimension_name": "",
                    "result_number": "", "result_name": "",
                    "result_name_html": "", "result_desc": "暂未获取到结果，请重新测试",
                    "result_desc_html": '[{\"type\": \"string\", \"value\": \"暂未获取到结果，请重新测试\"}]', "value": ""}
        dim_list.append(dim_data)
        res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img": background_img, "statement": statement,
               "result_img": result_img, "dim_list": dim_list, "title_img": title_img}
    ans_obj.result = res
    ans_obj.save()
    return


def count_finish_number(user_id, qt_id, ans_id):
    ans = UserAnswer.objects.filter(~Q(u_id=ans_id)).filter(qt_id=qt_id, user_id=user_id).first()
    if not ans: # 以前没有回答过该问卷才统计
        obj = UserAnswer.objects.filter(qt_id=qt_id, user_id=user_id, u_id=ans_id).first()
        if not obj.result: # 还没有生成结果
            q = QuestionType.objects.filter(u_id=qt_id).first()
            if q:
                old_finish_num = q.finish_number
                try:
                    old_finish_num = int(old_finish_num)
                except Exception as e:
                    old_finish_num = 0
                q.finish_number = old_finish_num + 1
                q.save()
            q_tmp = QuestionType_tmp.objects.filter(u_id=qt_id).first()
            if q_tmp:
                old_finish_num = q_tmp.finish_number
                try:
                    old_finish_num = int(old_finish_num)
                except Exception as e:
                    old_finish_num = 0
                q_tmp.finish_number = old_finish_num + 1
                q_tmp.save()
            return
        return

def count_show_number(request, qt_id):
    token = request.META.get('HTTP_AUTHORIZATION')
    user_id = get_user_id(token)
    sh = UserShow_number.objects.filter(qt_id=qt_id, user_id=user_id).first()
    if not sh: # 没有浏览过才增加
        q = QuestionType.objects.filter(u_id=qt_id).first()
        if q:
            old_show_number = q.show_number
            try:
                old_show_number = int(old_show_number)
            except Exception as e:
                old_show_number = 0
            q.show_number = old_show_number + 1
            q.save()
        q_tmp = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        if q_tmp:
            old_show_number = q_tmp.show_number
            try:
                old_show_number = int(old_show_number)
            except Exception as e:
                old_show_number = 0
            q_tmp.show_number = old_show_number + 1
            q_tmp.save()
        #添加完成将记录入库
        UserShow_number.objects.create(qt_id=qt_id, user_id=user_id)
        return
    else:  # 更新浏览时间
       sh.update_time = timezone.now()
       sh.save()
    return

def check_user_answer(request, qt_id):   # 判断用户是否回答过
    token = request.META.get('HTTP_AUTHORIZATION')
    user_id = get_user_id(token)
    obj = UserAnswer.objects.filter(qt_id=qt_id, user_id=user_id).order_by('-id').first()
    if obj:
        if obj.result:
            return True
        return False
    return False


def user_is_payed(user_id, qt_id, tmp):
    # 用户是否已支付问卷
    if tmp == "tmp":
        obj = Order_tmp.objects.filter(user_id=user_id, qt_id=qt_id, pay_status="已支付").last()
    else:
        obj = Order.objects.filter(user_id=user_id, qt_id=qt_id, pay_status="已支付").last()
    if obj:
        return True
    return False

def get_user_questions(user_id):
    result = []
    finish_dic = {}
    ans = UserAnswer.objects.filter(user_id=user_id)
    for a in ans:
        if a.result:
            finish_dic[a.qt_id] = {'qt_id': a.qt_id, 'ans_id': a.u_id}
    sh = UserShow_number.objects.filter(user_id=user_id).order_by('-update_time')
    for i in sh:
        qt = QuestionType.objects.filter(u_id=i.qt_id).first()
        if qt:
            item = {}
            item['u_id'] = i.qt_id
            item['ans_id'] = ""
            item['title'] = qt.title
            title_img = ""
            if qt.title_img:
                title_img = settings.DOMAIN + "/media/image/" + qt.title_img
            item['title_img'] = title_img
            is_payed = user_is_payed(user_id, i.qt_id, "used")
            item['is_payed'] = is_payed
            is_finish = False
            if finish_dic.get(i.qt_id):
                is_finish = True
                item['ans_id'] = finish_dic.get(i.qt_id, {}).get('ans_id', '')
            item['is_finish'] = is_finish
            item['amount'] = qt.amount
            item['pay_type'] = qt.pay_type
            result.append(item)
    return result

