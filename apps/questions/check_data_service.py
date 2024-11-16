from datetime import datetime
from apps.questions.models import Image, QuestionType_tmp, Question_tmp, Calculate_Exp_tmp
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

def check_add_question(data):
    qt_id = data.get("qt_id")
    questions = data.get('questions')
    o_number_list = [chr(x) for x in range(65, 85)]  # ABC...T
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if not qt:
        raise Exception_('问卷不存在！')
    index = 1
    for i in questions:
        number = i.get('number')
        q_type = i.get('q_type', '')
        qt_type = i.get('qt_type', '')
        q_options = i.get('q_options', [])
        if q_type:
            if q_type not in ['单选题', '多选题', '问答题']:
                raise Exception_('不支持该种题目类型！')
        if qt_type:
            if qt_type not in ['文本题', '语音题', '视频题']:
                raise Exception_('不支持该种题目类型！')
        try:
            if int(number) != index:
                raise Exception_(f'问题编号{index}错误！')
            index += 1
        except Exception as e:
            raise Exception_(f'不支持该题目编号{number}！')
        if len(q_options) > 20:
            raise Exception_('最多支持20个选项！')
        for j in q_options:
            o_number = j.get('o_number')
            if o_number not in o_number_list:
                raise Exception_(f'不支持的选项{o_number}')

def check_add_calculate(data):
    qt_id = data.get('qt_id')
    exp = data.get('exp', [])
    order = data.get('order')
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    ques = Question_tmp.objects.filter(qt_id=qt_id).values('u_id')
    q_id_list = []
    for q in ques:
        q_id_list.append(q['u_id'])
    if not qt:
        raise Exception_('问卷不存在！')
    if len(exp) > 300:
        raise Exception_('最多支持300个因子！')
    for e in exp:
        formula = e.get('formula',[])
        exp_name = e.get('exp_name','')
        for fm in formula:
            if fm.get('type') == "question_id":
                value = fm.get('value')
                if value not in q_id_list:
                    raise Exception_(f'{exp_name} 配置错误，请重新配置！')
    return


def check_add_result(data):
    qt_id = data.get('qt_id')
    results = data.get('results', [])
    exp_id_list = []
    exps = Calculate_Exp_tmp.objects.filter(qt_id=qt_id).values('u_id')
    for e in exps:
        exp_id_list.append(e['u_id'])
    qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
    if not qt:
        raise Exception_('问卷不存在！')
    if len(results) <= 0:
        raise Exception_('未配置问卷结果！')
    for i in results:
        dims = i.get('dimension', [])
        for j in dims:
            d_res = j.get('d_result', [])
            for k in d_res:
                value = k.get('value', {})
                result_name = k.get('result_name')
                factor_list = value.get('factor_list', [])
                for f in factor_list:
                    exp_id = f.get('exp_id')
                    if exp_id not in exp_id_list:
                        raise Exception_(f'{result_name} 配置错误，请重新配置！')
    return