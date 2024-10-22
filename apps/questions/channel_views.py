import uuid
from datetime import datetime

from rest_framework.response import Response
from apps.questions.models import Channel_tmp, ChannelData_tmp
from apps.questions.serizlizers import Channel_tmpListSerializers
from rest_framework.generics import CreateAPIView, ListAPIView

from apps.questions.services import copy_channel_tmp_table
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import isManagementPermission, idAdminAndCheckerPermission
from apps.users.utils import token_to_name


class ChannelView(CreateAPIView):
    queryset = Channel_tmp.objects.all()
    serializer_class = Channel_tmpListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        main_title = data.get('main_title')
        status = data.get('status')
        create_user = data.get('create_user')
        check_user = data.get('check_user')
        type = data.get('order')
        queryset = self.get_queryset()
        if main_title:
            queryset = queryset.filter(main_title=main_title)
        if status:
            queryset = queryset.filter(status=status)
        if create_user:
            queryset = queryset.filter(create_user=create_user)
        if check_user:
            queryset = queryset.filter(check_user=check_user)
        if type:
            queryset = queryset.filter(type=type)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChannelADDView(CreateAPIView, ListAPIView):
    queryset = Channel_tmp.objects.all()
    serializer_class = Channel_tmpListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        main_title = data.get('main_title', '')
        type = data.get('type')
        channels = data.get('channel', [])
        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        for i in channels:
            index = i.get('index', '')
            item = {}
            item['u_id'] = str(uuid.uuid4())
            item['index'] = i.get('index', '')
            item['qt_id'] = i.get('qt_id', '')
            item['source'] = i.get('source', '')
            item['type'] = type
            item['title'] = i.get('title', '')
            item['url'] = i.get('url', '')
            item['desc'] = i.get('desc', '')
            item['amount'] = i.get('amount', '')
            item['pay_type'] = i.get('pay_type', '')
            ChannelData_tmp.objects.update_or_create(index=index, type=type, defaults=item)
        defaults = {}
        defaults['u_id'] = str(uuid.uuid4())
        defaults['create_user'] = u_name
        defaults['update_user'] = u_name
        defaults['main_title'] = main_title
        defaults['type'] = type
        status = "草稿"
        obj = Channel_tmp.objects.filter(type=type).first()
        if obj:
            if obj.status == "审批拒绝":
                status = "草稿"
            elif obj.status in ["已上线", "已上线（草稿审核拒绝）", "已上线（有草稿）"]:
                status = "已上线（有草稿）"
            elif obj.status == "已下线":
                status = "草稿"
            else:
                status = "草稿"
        defaults['status'] = status
        Channel_tmp.objects.update_or_create(type=type, defaults=defaults)
        return Response({"detail": "success"})

    def list(self, request, *args, **kwargs):
        type = request.query_params.get('type')
        if type:
            obj = Channel_tmp.objects.filter(type=type).first()
            ds = ChannelData_tmp.objects.filter(type=type)
            item_list = []
            for j in ds:
                c = {
                    "index": j.index,
                    "qt_id": j.qt_id,
                    "source": j.source,
                    "title": j.title,
                    "url": j.url,
                    "desc": j.desc,
                    "amount": j.amount,
                    "pay_type": j.pay_type
                }
                item_list.append(c)
            main_title = obj.main_title if obj else ""
            type = obj.type if obj else ""
            data = {"main_title": main_title, 'type':type, 'channel': item_list}
        else:
            data = []
            channels = Channel_tmp.objects.all()
            for i in channels:
                type = i.type
                item = {}
                item['main_title'] = i.main_title
                item['type'] = type
                ds = ChannelData_tmp.objects.filter(type=type)
                item_list = []
                for j in ds:
                    c = {
                        "index": j.index,
                        "qt_id": j.qt_id,
                        "source": j.source,
                        "title": j.title,
                        "url": j.url,
                        "desc": j.desc,
                        "amount": j.amount,
                        "pay_type": j.pay_type
                    }
                    item_list.append(c)
                item['channel'] = item_list
                data.append(item)
        return Response(data=data)

class ChannelSubmitView(CreateAPIView):
    queryset = Channel_tmp.objects.all()
    serializer_class = Channel_tmpListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        type = data.get('type')
        obj = Channel_tmp.objects.filter(type=type).first()
        if obj:
            if obj.status == "草稿":
                obj.status = "待审核"
                obj.save()
                return Response({"detail": "success"})
            if obj.status == "已上线（有草稿）":
                obj.status = "已上线（草稿待审核）"
                obj.save()
                return Response({"detail": "success"})
        return Response({"detail": "该频道不存在！"}, status=400)


class ChannelCheckView(CreateAPIView):
    queryset = Channel_tmp.objects.all()
    serializer_class = Channel_tmpListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (idAdminAndCheckerPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        type = data.get('type')
        status = data.get('status')
        obj = Channel_tmp.objects.filter(type=type).first()
        check_time = datetime.now()
        check_user = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        if not obj:
            return Response({"detail": "频道不存在！"}, status=400)
        if obj.status_tmp not in ["待审核", "已上线（草稿待审核）"]:
            return Response({"detail": "非待审核数据不支持操作！"}, status=400)
        if status == "审核拒绝":
            t_status = "审核拒绝"
            if obj.status == "已上线（草稿待审核）":
                t_status = "已上线（草稿审核拒绝）"
            Channel_tmp.objects.filter(type=type).update(status=t_status, check_user=check_user)
            return Response({"detail": "success"})
        if status == "已上线":
            Channel_tmp.objects.filter(type=type).update(status="已上线", check_user=check_user)
            copy_channel_tmp_table(type)
            return Response({"detail": "success"})
        return Response({"detail": "参数错误！"}, status=400)