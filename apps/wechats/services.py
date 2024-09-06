import re

from django.conf import settings

from apps.questions.models import Dimension, Question, Option, Calculate_Exp, Result_Title
from apps.users.exceptions import Exception_
from apps.wechats.models import UserAnswer
format_dic = {"大于": ">", "大于等于": ">=",
              "小于": "<", "小于等于": "<=",
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
    for q_id,v in answer.items():
        o_number = v.get('o_number')
        obj = Option.objects.filter(q_id=q_id, o_number=o_number).first()
        if obj:
            value = obj.value
            try:
                int(value)  # 数值计算
                result[q_id] = value
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
    ans_data = generate_user_answer_data(answer)
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
                for r in res: # 将所以的变量都替换为值
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
    res = {"r_u_id": r_u_id, "qt_id": qt_id, "background_img":background_img, "statement":statement,
           "result_img": result_img, "dim_list": dim_list}
    ans_obj.result = res
    ans_obj.save()
    return

