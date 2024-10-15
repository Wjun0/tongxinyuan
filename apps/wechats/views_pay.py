import uuid
from django.conf import settings
from rest_framework.generics import ListAPIView, CreateAPIView
from apps.questions.models import QuestionType_tmp, QuestionType
from apps.users.permission import WexinPermission
from apps.users.utils import get_user_id
from rest_framework.response import Response
from apps.wechats.models import Order_tmp, Order
from apps.wechats.pay import pay_jsapi, notify_callback, query
import logging
LOG = logging.getLogger('log')

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
        title = qt.title
        result, out_trade_no  = pay_jsapi(user_id, title, amount)  # 微信下单接口
        if result.get('detail') == "success":
            if tmp == "tmp":
                Order_tmp.objects.create(u_id=out_trade_no, user_id=user_id, qt_id=qt_id, title=title, pay_status="待支付")
            else:
                Order.objects.create(u_id=out_trade_no, user_id=user_id, qt_id=qt_id, title=title, pay_status="待支付")
        return Response(result)

class NotifyView(CreateAPIView):

    def create(self, request, *args, **kwargs):
        LOG.info(f"支付回调通知 \r\n {request.headers} \r\n {request.data}")
        result = notify_callback(request.headers, request.data)
        LOG.info(f"notify_callback =  \r\n {result}")
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
            LOG.info(f"支付回调成功 \r\n out_trade_no={out_trade_no}")
            return Response({"message": "success"})
        s = {'id': 'a5657519-b2c1-5f1f-b919-26cf57995de6', 'create_time': '2024-10-09T17:57:42+08:00',
         'resource_type': 'encrypt-resource', 'event_type': 'TRANSACTION.SUCCESS', 'summary': '支付成功',
         'resource': {'original_type': 'transaction', 'algorithm': 'AEAD_AES_256_GCM',
                      'ciphertext': 'LblphfIG79IW638A06YFXaQVXi3gsZ+NgYOd4j5k7kRZwy8+GmQvpaTzvOR2UZhPGH81vd2kTQoXWRhydBVCybaKKeKbTktWeMmBwO7xWB5v4R139zy/0bjlzVjNxq93CHOuPtaPBVqAiFo6dUAnGknoR8anfwEXxTa4vM+1VfpO5iBgnAP8lLcc1za3gUk9OvF8lGgtaDdsbBZ/xwhl+cF5H/tjmdvLppnkp5yE8/E1nDQcFtxWlRpiq5sXhyzzPqNQDO9xNLR58wzTD+zlabNh9+EyXjL3MemQGUymKgMmR+rPQZeuxbiZW4KHWAsgHkMolRfLNtRBSG6gIciRObNOR1rMEr47WNTn3kzb8vkZIyj8jnfH1EzRfVU3+FxHzQVZUoUHNIqTkEfRc8SZLwNBjZ/O9WBT+l2HUXBvM54RXJCd9x6IPLMttJslkDiey5S0AUT3vDRlG4JH4DaxsOltbFYHIgpMHX9jEhzlZOTRijyn3tX8KKbaWFEoj4kvrs2zIKPskv3a0WXTy+xWEqHFLubXGQOKQPIyd0ITrmu56KHLHlVNZ15OD3OOxPZcfpo=',
                      'associated_data': 'transaction', 'nonce': 'HogZtBg3vfzW'}}
        LOG.info(f"支付回调失败 \r\n result={result}")
        return Response({"message": "fail"}, status=200)

class PayQueryView(CreateAPIView):
    permission_classes = (WexinPermission,)

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        user_id = get_user_id(token)
        qt_id = request.data.get('u_id', '')
        tmp = request.data.get('tmp', '')
        if tmp == "tmp":
            obj = Order_tmp.objects.filter(user_id=user_id, qt_id=qt_id, pay_status="待支付").last()
        else:
            obj = Order.objects.filter(user_id=user_id, qt_id=qt_id, pay_status="待支付").last()
        if not obj:
            return Response({"detail": "fail", "data": {"reson": "未找到支付订单！"}})
        code, message = query(obj.u_id)
        LOG.info(f'查询订单状态 code={code}, message={message}')
        if code in range(200,300):
            trade_state_desc = eval(message).get('trade_state_desc')
            if trade_state_desc == "订单未支付":
                return Response({"detail": "fail", "data": {"pay_status": "订单未支付"}})
            elif trade_state_desc == "支付成功":
                obj.pay_status = "已支付"
                obj.save()
                return Response({"detail": "success", "data":{"pay_status":"支付成功"}})
            else:
                return Response({"detail": "fail", "data": {"pay_status": "其他"}})
        return Response({"detail": "fail", "data": {"pay_status": "订单未支付"}})
