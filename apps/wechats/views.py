import base64
import logging
import re
import time
import uuid
from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from weixin import WXAPPAPI

from apps.questions.models import QuestionType, Question, Option, QuestionType_tmp, Question_tmp, Option_tmp, Channel, \
    ChannelData
from apps.users.models import User
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import WexinPermission
from apps.users.utils import get_user_id
from apps.wechats.models import UserAnswer, UserAnswer_tmp
from apps.wechats.serizlizers import QuestionTypeListSerializers
from apps.wechats.services import generate_result, count_finish_number, count_show_number, check_user_answer, \
    user_is_payed, get_user_questions
from apps.wechats.tmp_service import get_tmp_result, get_user_tmp_answer_result
from utils.generate_jwt import generate_jwt


class LoginAPIView(CreateAPIView):

    def post(self, request, *args, **kwargs):
        """
         weixin api 获取code
        """
        code = request.data.get('code')
        try:
            api = WXAPPAPI(appid=settings.WX_APPID, app_secret=settings.WX_SECRET)
            info = api.exchange_code_for_session_key(code=code)
            print(info)
            session_key = info.get('session_key')
            openid = info.get('openid')
            user_info = {"user_id": openid, "iat": time.time()}
            access_token = generate_jwt(user_info, 24)
            refresh_token = generate_jwt(user_info, 24)
            print(f"token={access_token}")
            d = {"role": 100, "token": access_token, "status": "used", "token_exp": datetime.now()}
            User.objects.update_or_create(user_id=openid, defaults=d)
            return Response({"detail": "success", "data":{"access_token": access_token, "refresh_token": refresh_token}})
        except Exception as e:
            logger = logging.getLogger("log")
            logger.error(e)
            return Response({"detail": "fail", "data": "无效的code"})

class GetPhoneAPIView(CreateAPIView, ListAPIView):
    permission_classes = (WexinPermission,)

    def list(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return Response({'detail': "fail",'data': "用户不存在！"})
        return Response({"detail": "success", "data": {"phone": user.mobile}})


    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        try:
            # api = WXAPPAPI(appid=settings.WX_APPID, app_secret=settings.WX_SECRET)
            # info = api.exchange_code_for_session_key(code=code)
            token = request.META.get('HTTP_AUTHORIZATION')
            user_id = get_user_id(token)
            url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={settings.WX_APPID}&secret={settings.WX_SECRET}"
            a_resp = requests.get(url)
            access_token = a_resp.json().get('access_token')
            get_phone_url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
            resp = requests.post(get_phone_url, json={"code": code}, headers={"Content-Type": "application/json"})
            phone = resp.json().get('phone_info', {}).get('phoneNumber')
            User.objects.filter(user_id=user_id).update(mobile=phone)
            return Response({"detail": "success", "data":{"phone": phone}})
        except Exception as e:
            logger = logging.getLogger("log")
            logger.error(e)
            return Response({"detail": "fail", "data": "获取手机号失败！"})


class UserInfoAPIView(ListAPIView):
    permission_classes = (WexinPermission,)

    def list(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return Response({'detail': "fail", 'data': "用户不存在！"})
        data = {}
        data['user_id'] = user_id
        data['user_name'] = user.user_name
        data['phone'] = user.mobile
        questions = get_user_questions(user_id)
        data['questions'] = questions
        return Response({"detail": "success", "data": data})

class ChangeUsernameAPIView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def post(self, request, *args, **kwargs):
        data = request.data
        user_name = data.get('user_name')
        if not user_name:
            return Response({'detail': "fail", 'data': "用户名不能为空！"})
        if len(user_name) > 20:
            return Response({'detail': "fail", 'data': "用户名长度大于20个字符！"})
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return Response({'detail': "fail", 'data': "用户不存在！"})
        user.user_name = user_name
        user.save()
        return Response({"detail": "success", "data": data})

class ChangePhoneAPIView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def post(self, request, *args, **kwargs):
        data = request.data
        phone = data.get('phone')
        if not phone:
            return Response({'detail': "fail", 'data': "手机号不能为空！"})
        mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57]|19[012356789])[0-9]{8}$')
        if not mobile_re.match(phone):
            return Response({'detail': "fail", 'data': "错误的手机号！"})
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        user = User.objects.filter(user_id=user_id).first()
        if not user:
            return Response({'detail': "fail", 'data': "用户不存在！"})
        user.mobile = phone
        user.save()
        return Response({"detail": "success", "data": data})


class IndexView(ListAPIView):
    queryset = QuestionType.objects.filter(status="已上线").order_by('-update_time')
    serializer_class = QuestionTypeListSerializers
    # filterset_class = QuestionTypeFilter
    pagination_class = ResultsSetPagination
    permission_classes = (WexinPermission,)

class DetailView(ListAPIView):
    queryset = QuestionType.objects.filter(status="已上线").order_by('update_time')
    permission_classes = (WexinPermission,)

    def list(self, request, *args, **kwargs):
        data = request.query_params
        qt_id = data.get("u_id")
        tmp = data.get("tmp")
        user_id = get_user_id(request.META.get('HTTP_AUTHORIZATION'))
        is_payed = user_is_payed(user_id, qt_id, tmp)
        if tmp == "tmp":  # 获取临时问卷，测试答题
            result = get_tmp_result(qt_id, is_payed)
            return Response({"detail": "success", "data": result, "user_is_answer": False})
        qt = self.get_queryset().filter(u_id=qt_id).first()
        if not qt:
            return Response({"detail": "fail！", "data": "问卷不存在！"})
        # now = timezone.now()
        # if now < qt.start_time:
        #     return Response({"detail": "问卷即将开放，敬请期待~"}, status=403)
        # if now > qt.end_time:
        #     return Response({"detail": "问卷已下线，去看看其他有趣内容吧~"}, status=403)
        background_img = qt.background_img
        if background_img:
            background_img = settings.DOMAIN + "/media/image/" + background_img
        title_img = qt.title_img
        if title_img:
            title_img = settings.DOMAIN + "/media/image/" + title_img
        result = {"qt_id": qt.u_id, "background_img": background_img, 'title_img': title_img,
                  "title": qt.title, "test_value": qt.test_value, "test_value_html": qt.test_value_html,
                  'q_number': qt.q_number, "test_time": qt.test_time, "use_count": qt.use_count, 'source':qt.source,
                  'pay_type': qt.pay_type, 'amount': qt.amount, 'is_payed': is_payed}
        count_show_number(request, qt_id)
        user_is_answer = check_user_answer(request, qt_id)
        return Response({"detail": "success", "data": result, "user_is_answer": user_is_answer})

class GETQuestionView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def get_result(self, tmp, qt_id, order, end_num, number="1"):
        if tmp == "tmp":
            obj = Question_tmp.objects.filter(qt_id=qt_id, number=number).first()
        else:
            obj = Question.objects.filter(qt_id=qt_id, number=number).first()
        if not obj:
            return {}  # 最后一题
        options = []
        if tmp =="tmp":
            op = Option_tmp.objects.filter(q_id=obj.u_id)
        else:
            op = Option.objects.filter(q_id=obj.u_id)
        for i in op:
            options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
        result = {"q_id": obj.u_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr,
                  "number": obj.number, "end_number": end_num, "order": order,
                  'q_title': obj.q_title, 'q_title_html': obj.q_title_html, "options": options}
        return result

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('u_id')
        last_number = data.get('last_number')
        last_q_id = data.get('last_q_id')
        last_o_number = data.get('last_o_number', '')
        tmp = data.get('tmp', '')
        if tmp =="tmp":
            qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        else:
            qt = QuestionType.objects.filter(u_id=qt_id).first()
        title = ''
        if not qt:
            return Response({"detail": "fail", "data": "问卷不存在！"})
        else:
            title = qt.title
        if qt.pay_type == "付费":
            user_id = get_user_id(request.META.get('HTTP_AUTHORIZATION'))
            is_payed = user_is_payed(user_id, qt_id, tmp)
            if not is_payed:
                return Response({"detail": "fail", "data": "问卷未支付！"})
            # 判断题目是否是顺序题
        if tmp =="tmp":
            q = Question_tmp.objects.filter(qt_id=qt_id).values('u_id')
        else:
            q = Question.objects.filter(qt_id=qt_id).values('u_id')
        q_u_id_list = []
        for i in q:
            q_u_id_list.append(i['u_id'])
        if tmp == "tmp":
            ops = Option_tmp.objects.filter(q_id__in=q_u_id_list)
        else:
            ops = Option.objects.filter(q_id__in=q_u_id_list)
        end_num = str(len(q))
        order = False
        for j in ops:
            if j.next_q_id and j.next_q_id !=0: # 有排序
                order = True
                break
        if not last_q_id and not last_o_number:
            # 获取第一题
            result = self.get_result(tmp, qt_id, order, end_num, number="1")
            return Response({"detail": "success", "data": result, 'title': title})
        if tmp == "tmp":
            l_q = Question_tmp.objects.filter(qt_id=qt_id, number=last_number).first()
        else:
            l_q = Question.objects.filter(qt_id=qt_id, number=last_number).first()
        if not l_q:
            Response({"detail": "fail", "data": "找不到上一题的数据！"})
        if l_q.q_type == "问答题":
            # 没有定义下一题
            number = int(last_number) + 1
            result = self.get_result(tmp, qt_id, order, end_num, number=str(number))
            return Response({"detail": "success", "data": result, 'title': title})

        if  ',' in last_o_number: # 如果是多选题，按第一个选项的顺序跳转
            last_o_number = last_o_number.split(',')[0]
        if tmp == "tmp":
            obj = Option_tmp.objects.filter(q_id=last_q_id, o_number=last_o_number).first()
        else:
            obj = Option.objects.filter(q_id=last_q_id, o_number=last_o_number).first()
        if not obj:
            return Response({"detail": "fail", "data": "题目未找到！"})
        if not obj.next_q_id or obj.next_q_id==0:
            # 没有定义下一题
            number = int(last_number) + 1
            result = self.get_result(tmp, qt_id, order, end_num, number=str(number))
            return Response({"detail": "success", "data": result, 'title': title})
        else:  # 根据上一题获取下一题
            if tmp == "tmp":
                obj = Question_tmp.objects.filter(qt_id=qt_id, u_id=obj.next_q_id).first()
            else:
                obj = Question.objects.filter(qt_id=qt_id, u_id=obj.next_q_id).first()
            if not obj:
                return Response({"detail": "success", "data": {}})
            options = []
            if tmp == "tmp":
                op = Option_tmp.objects.filter(q_id=obj.u_id)
            else:
                op = Option.objects.filter(q_id=obj.u_id)
            for i in op:
                options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
            result = {"q_id": obj.u_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr, "number": obj.number,
                      "end_number": end_num, "order": order, 'q_title': obj.q_title,
                        'q_title_html': obj.q_title_html, "options": options}
            return Response({"detail": "success", "data": result, 'title': title})

class QuestionView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('u_id')
        q_id = data.get('q_id')
        o_number = data.get('o_number','')
        text = data.get('text','')
        ans_id = data.get('ans_id','')
        tmp = data.get('tmp','')
        if not(qt_id and q_id):
            return Response({"detail": "fail",  "data": "参数错误！"})
        if tmp == "tmp":
            obj = Question_tmp.objects.filter(u_id=q_id, qt_id=qt_id).first()
            qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        else:
            obj = Question.objects.filter(u_id=q_id, qt_id=qt_id).first()
            qt = QuestionType.objects.filter(u_id=qt_id).first()
        if not obj or not qt:
            return Response({"detail": "fail！", "data": "回答问题不存在！"})
        if qt.pay_type == "付费":
            user_id = get_user_id(request.META.get('HTTP_AUTHORIZATION'))
            is_payed = user_is_payed(user_id, qt_id, tmp)
            if not is_payed:
                return Response({"detail": "fail", "data": "问卷未支付！"})
        if obj.q_check_role == "性别校验":
            sex = obj.sex
            if tmp == "tmp":
                op = Option_tmp.objects.filter(q_id=q_id, o_number=o_number).first()
            else:
                op = Option.objects.filter(q_id=q_id, o_number=o_number).first()
            if sex != op.o_content:
                return Response({"detail": "fail", "data": {"message": "答题结果不符合性别要求！"}})
        if obj.q_check_role == "年龄校验":
            min_age = obj.min_age
            max_age = obj.max_age
            if tmp == "tmp":
                op = Option_tmp.objects.filter(q_id=q_id, o_number=o_number).first()
            else:
                op = Option.objects.filter(q_id=q_id, o_number=o_number).first()
            o_content = op.o_content
            user_min = o_content.split('-')[0]
            user_max = o_content.split('-')[1]
            if "不限" in user_max:
                user_max = 1000
            if "以上" in max_age:
                max_age = 1000
            if int(user_min) < int(min_age) or int(user_max) > int(max_age):
                return Response({"detail": "fail", "data": {"message": "答题结果不符合年龄要求！"}})
        if obj.q_type == "单选题":
            # if o_number not in ["A", 'B', 'C', 'D', 'E', 'F']:
            if o_number not in [chr(i) for i in range(65, 85)]:
                return Response({"detail": "fail","data": "不存在该选项！"})
        if obj.q_type == "多选题":
            o_number_list = o_number.split(',')
            for i in o_number_list:
                if i not in [chr(i) for i in range(65, 85)]:
                    return Response({"detail": "fail", "data": "错误的选项！"})
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        if not ans_id:
            ans_id = str(uuid.uuid4())
            an = {q_id: {"o_number": o_number, "text": text}}
            default = {"u_id": ans_id, 'user_id': user_id, 'qt_id':qt_id, "answer": an, "result": {}}
            if tmp == "tmp":
                UserAnswer_tmp.objects.update_or_create(u_id=ans_id, user_id=user_id, qt_id=qt_id, defaults=default)
            else:
                UserAnswer.objects.update_or_create(u_id=ans_id, user_id=user_id, qt_id=qt_id, defaults=default)
            return Response({"detail": "success", "data": {"ans_id": ans_id}})
        if tmp == "tmp":
            obj = UserAnswer_tmp.objects.filter(u_id=ans_id, user_id=user_id, qt_id=qt_id).first()
        else:
            obj = UserAnswer.objects.filter(u_id=ans_id, user_id=user_id, qt_id=qt_id).first()
        if not obj:
            return Response({"detail": "fail", "data": "参数错误！"})
        answer = obj.answer
        answer[q_id] = {"o_number": o_number, "text": text}
        obj.answer = answer
        obj.save()
        return Response({"detail": "success", "data": {"ans_id": ans_id}})

class ResultView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('u_id','')
        ans_id = data.get('ans_id', '')
        tmp = data.get('tmp', '')
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        if tmp == "tmp":
            res = get_user_tmp_answer_result(data, user_id)
            return Response(res)
        qt = QuestionType.objects.filter(u_id=qt_id).first()
        if not qt:
            title = ''
        else:
            title = qt.title
        if not ans_id: # 没有ans_id 获取历史的问卷结果
            obj = UserAnswer.objects.filter(qt_id=qt_id, user_id=user_id).order_by('-update_time').first()
            if not obj:
                result = {}
            else:
                result = obj.result
            return Response({"detail": "success", "data": result, 'title':title})
        # 统计完成数据,必须在生成结果前统计
        count_finish_number(user_id, qt_id, ans_id)
        generate_result(qt_id, ans_id)
        # 生成结果
        obj = UserAnswer.objects.filter(u_id=ans_id, qt_id=qt_id).first()
        if not obj:
            result = {}
        else:
            result = obj.result
        return Response({"detail": "success", "data": result, 'title': title})


class ChannelAPIView(ListAPIView):
    queryset = Channel.objects.all()
    permission_classes = (WexinPermission,)

    def list(self, request, *args, **kwargs):
        type = request.query_params.get('type')
        data = {}
        if type:
            obj = self.get_queryset().filter(type=type, status="已上线").first()
            if obj:
                data['main_title'] = obj.main_title
                data['type'] = obj.type
                data['status'] = obj.status
                data['status'] = obj.status
                channels = []
                chas = ChannelData.objects.filter(type=type)
                for i in chas:
                    item = {}
                    item['index'] = i.index
                    item['qt_id'] = i.qt_id
                    item['source'] = i.source
                    item['title'] = i.title
                    img = ""
                    if i.img:
                        img = settings.DOMAIN + "/media/image/" + i.img
                    item['img'] = img
                    item['url'] = i.url
                    item['type'] = i.type
                    item['desc'] = i.desc
                    item['amount'] = i.amount
                    item['pay_type'] = i.pay_type
                    channels.append(item)
                data['channels'] = channels
        return Response({"detail": "success", "data": data})