import base64
import logging
import time
import uuid
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from weixin import WXAPPAPI

from apps.questions.models import QuestionType, Question, Option
from apps.users.models import User
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import WexinPermission
from apps.users.utils import get_user_id
from apps.wechats.models import UserAnswer
from apps.wechats.serizlizers import QuestionTypeListSerializers
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
            d = {"role": 100, "token": access_token, "status": "used", "token_exp": datetime.now()}
            User.objects.update_or_create(user_id=openid, defaults=d)
            return Response({"detail": "success", "data":{"access_token": access_token, "refresh_token": refresh_token}})
        except Exception as e:
            logger = logging.getLogger("log")
            logger.error(e)
            return Response({"detail": "无效的code"}, status=400)

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
        qt = self.get_queryset().filter(u_id=qt_id).first()
        if not qt:
            return Response({"detail": "问卷不存在！"}, status=400)
        now = timezone.now()
        if now < qt.start_time:
            return Response({"detail": "问卷即将开放，敬请期待~"}, status=403)
        if now > qt.end_time:
            return Response({"detail": "问卷已下线，去看看其他有趣内容吧~"}, status=403)
        result = {"qt_id": qt.u_id, "background_img": qt.background_img, 'title_img': qt.title_img,
                  "title": qt.title, "test_value": qt.test_value, "test_value_html": qt.test_value_html,
                  'q_number': qt.q_number, "test_time": qt.test_time, "use_count": qt.use_count, 'source':qt.source}
        return Response({"detail": "success", "data": result})

class QuestionView(ListAPIView, CreateAPIView):
    permission_classes = (WexinPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('u_id')
        q_id = data.get('q_id')
        o_number = data.get('o_number')
        ans_id = data.get('ans_id','')
        if not(qt_id and q_id and o_number):
            return Response({"detail": "参数错误！"}, status=400)
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        if not ans_id:
            ans_id = str(uuid.uuid4())
            an = {"answer": [{"q_id": q_id, "o_number": o_number}]}
            default = {"u_id": ans_id, 'user_id': user_id, 'qt_id':qt_id, "answer": an, "result": {}}
            UserAnswer.objects.update_or_create(u_id=ans_id, user_id=user_id, qt_id=qt_id, defaults=default)
            return Response({"detail": "success", "data": {"ans_id": ans_id}})
        obj = UserAnswer.objects.filter(u_id=ans_id, user_id=user_id, qt_id=qt_id).first()
        if not obj:
            return Response({"detail": "参数错误！"}, status=400)
        answer = obj.answer.get("answer").append({"q_id": q_id, "o_number": o_number})
        # obj.answer = {"answer": answer}
        obj.save()
        return Response({"detail": "success", "data": {"ans_id": ans_id}})


    def get_result(self, qt_id, number):
        obj = Question.objects.filter(qt_id=qt_id, number=number).first()
        if not obj:
            return {}  # 最后一题
        options = []
        op = Option.objects.filter(q_id=obj.u_id)
        for i in op:
            options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
        result = {"q_id": obj.u_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr, "number": obj.number,
                  'q_title': obj.q_title, 'q_title_html': obj.q_title_html, "options": options, "q_number": obj.q_number}
        return result

    def list(self, request, *args, **kwargs):
        data = request.query_params
        qt_id = data.get('u_id')
        last_number = data.get('last_number')
        last_q_id = data.get('last_q_id')
        last_o_number = data.get('last_o_number')
        if not last_q_id and not last_o_number:
            # 获取第一题
            result = self.get_result(qt_id, number="1")
            return Response({"detail": "success", "data": result})
        obj = Option.objects.filter(q_id=last_q_id, o_number=last_o_number).first()
        if not obj:
            return Response({"detail": "找不到对应的数据"}, status=400)
        if not obj.next_q_id or obj.next_q_id==0:
            # 没有定义下一题
            number = int(last_number) + 1
            result = self.get_result(qt_id, number=str(number))
            return Response({"detail": "success", "data": result})
        else:  # 根据上一题获取下一题
            obj = Question.objects.filter(qt_id=qt_id, u_id=last_q_id).first()
            if not obj:
                return Response({"detail": "success", "data": {}})
            options = []
            op = Option.objects.filter(q_id=obj.u_id)
            for i in op:
                options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
            result = {"q_id": obj.q_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr, "number": obj.number,
                      'q_title': obj.q_title, 'q_title_html': obj.q_title_html, "options": options, "q_number": obj.q_number}
            return Response({"detail": "success", "data": result})