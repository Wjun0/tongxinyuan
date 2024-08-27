import base64
import logging
import time
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from weixin import WXAPPAPI

from apps.questions.models import QuestionType, Question, Option
from apps.users.models import User
from apps.users.pagenation import ResultsSetPagination
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
            logger = logging.getLogger(__name__)
            logger.error(e)
            return Response({"detail": "无效的code"}, status=400)

class IndexView(ListAPIView):
    queryset = QuestionType.objects.order_by('-update_time')
    serializer_class = QuestionTypeListSerializers
    # filterset_class = QuestionTypeFilter
    pagination_class = ResultsSetPagination
    # permission_classes = (isManagementPermission,)

class DetailView(ListAPIView):
    queryset = QuestionType.objects.order_by('update_time')

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
        return Response({"detail": "success", "result": result})

class QuestionView(ListAPIView, CreateAPIView):

    def create(self, request, *args, **kwargs):
        return

    def get_result(self, qt_id, number):
        obj = Question.objects.filter(qt_id=qt_id, number=number).first()
        if not obj:
            return Response({})  # 最后一题
        options = []
        op = Option.objects.filter(q_id=obj.u_id)
        for i in op:
            options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
        result = {"q_id": obj.q_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr, "number": obj.number,
                  'q_title': obj.q_title, 'q_title_html': obj.q_title_html, "options": options}
        return result

    def list(self, request, *args, **kwargs):
        data = request.query_param
        qt_id = data.get('qt_id')
        last_number = data.get('last_number')
        last_q_id = data.get('last_q_id')
        last_o_number = data.get('last_o_number')
        if not last_q_id and not last_o_number:
            # 获取第一题
            result = self.get_result(qt_id, number="1")
            return Response({"detail": "success", "result": result})
        obj = Option.objects.filter(q_id=last_q_id, o_number=last_o_number).first()
        if not obj.next_q_id or obj.next_q_id==0:
            # 没有定义下一题
            number = int(last_number) + 1
            result = self.get_result(qt_id, number=str(number))
            return Response({"detail": "success", "result": result})
        else:  # 根据上一题获取下一题
            obj = Question.objects.filter(qt_id=qt_id, u_id=last_q_id).first()
            if not obj:
                return Response({"detail": "success", "result": {}})
            options = []
            op = Option.objects.filter(q_id=obj.u_id)
            for i in op:
                options.append({"o_number": i.o_number, "o_content": i.o_content, "o_html_content": i.o_html_content})
            result = {"q_id": obj.q_id, 'q_type': obj.q_type, 'q_attr': obj.q_attr, "number": obj.number,
                      'q_title': obj.q_title, 'q_title_html': obj.q_title_html, "options": options}
            return Response({"detail": "success", "result": result})