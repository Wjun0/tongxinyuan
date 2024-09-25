import uuid

from django.conf import settings
from rest_framework.generics import ListAPIView, CreateAPIView
from apps.questions.models import QuestionType_tmp, QuestionType
from apps.users.permission import WexinPermission
from apps.users.utils import get_user_id
from rest_framework.response import Response
from apps.wechats.models import Order_tmp
from apps.wechats.pay import pay_jsapi, notify_callback


class PayJsApiView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        qt_id = request.data.get('u_id', '')
        tmp = request.data.get('tmp', '')
        if tmp == "tmp":
            qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        else:
            qt = QuestionType.objects.filter(u_id=qt_id).first()
        if not qt:
            return Response({"detail": "fail", "data": {"result": "问卷不存在！"}})
        amount = qt.amount
        result = pay_jsapi(user_id, qt.title, amount)  # 微信下单接口
        if result.get('detail') == "success":
            # 保存订单
            u_id = str(uuid.uuid4())

            Order_tmp.objects.create()
        return Response(result)


class NotifyView(CreateAPIView):

    def create(self, request, *args, **kwargs):
        result = notify_callback(request.headers, request.data)
        if result and result.get('event_type') == 'TRANSACTION.SUCCESS':
            resp = result.get('resource')
            appid = resp.get('appid')
            mchid = resp.get('mchid')
            out_trade_no = resp.get('out_trade_no')
            transaction_id = resp.get('transaction_id')
            trade_type = resp.get('trade_type')
            trade_state = resp.get('trade_state')
            trade_state_desc = resp.get('trade_state_desc')
            bank_type = resp.get('bank_type')
            attach = resp.get('attach')
            success_time = resp.get('success_time')
            payer = resp.get('payer')
            amount = resp.get('amount').get('total')
            return Response({"message": "success"})
        return Response({"message": "fail"}, status=500)