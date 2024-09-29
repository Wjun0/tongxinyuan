import datetime
import uuid

from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.models import QuestionType, Question, Calculate_Exp, Option, QuestionType_tmp, Question_tmp, \
    Option_tmp
from apps.questions.serizlizers import QuestionTypeTMPListSerializers, \
    QuestionTypeTMPSerializers, QuestionTMPSerializers
from apps.questions.services import add_question_type, add_question, add_order_and_select_value, \
    add_calculate, add_result, show_result, get_option_data, get_calculate, copy_tmp_table, get_question_option, \
    copy_use_table, get_add_result, copy_question
from apps.questions.services_show import get_show_question
from apps.questions.upload_image_service import upload
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import isManagementPermission, idAdminAndCheckerPermission
from apps.users.permission_utils import user_is_operator
from apps.users.utils import token_to_name


class UploadImage(CreateAPIView):
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        file_id, file_name = upload(request)
        return Response({"file_id": file_id, "file_name": file_name})

class ADDQuestionsTypeView(CreateAPIView, ListAPIView):
    queryset =  QuestionType.objects.order_by('id')
    serializer_class = QuestionTypeTMPSerializers
    permission_classes = (isManagementPermission,)

    def list(self, request, *args, **kwargs):
        qt_id = request.query_params.get("qt_id")
        qt = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        if not qt:
            return Response({"detail": "数据不存在！"}, status=400)
        queryset = QuestionType_tmp.objects.filter(u_id=qt_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not add_question_type(request):
            return Response({"detail": "参数错误！"}, status=400)
        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        data = request.data
        u_id = data.get('qt_id', '')
        pay_type = data.get('pay_type', '')
        amount = data.get('amount', '')
        if pay_type == "付费":
            amount = f'{float(amount):.2f}'
        else:
            amount = 0
        qt = QuestionType_tmp.objects.filter(u_id=u_id).first()
        if qt:
            if qt.status not in ["草稿", "审批拒绝", "已上线", "已上线（有草稿）", "已上线（草稿审核拒绝）", "已下线"]:
                return Response({"detail": "该状态不支持编辑！"}, status=400)
            if qt.status == "审批拒绝":
                status_tmp = "草稿"
            elif qt.status in ["已上线", "已上线（草稿审核拒绝）", "已上线（有草稿）"]:
                status_tmp = "已上线（有草稿）"
            elif qt.status == "已下线":
                status_tmp = "草稿"
            else:
                status_tmp = "草稿"
            data['status_tmp'] = status_tmp
            data['update_user'] = u_name
            data['amount'] = amount
            QuestionType_tmp.objects.update_or_create(u_id=u_id, defaults=data)
            return Response({"detail": "success", 'result': {'title': data.get('title')}})
        # else: # 新增逻辑
        uid = str(uuid.uuid4())
        del data['qt_id']
        data['status'] = "草稿"
        data['status_tmp'] = "草稿"
        data['u_id'] = uid
        data['create_user'] = u_name
        data['update_user'] = u_name
        data['start_time'] = "2024-01-01 12:12:12"      # 暂时不用的字段
        data['end_time'] = "2044-12-12 12:12:12"        # 暂时不用的字段
        data['show_number'] = 0
        data['finish_number'] = 0
        res = QuestionType_tmp.objects.create(**data)
        result = {"u_id":res.u_id, "background_img": res.background_img, "title": res.title}
        return Response({"detail": "success", "result": result})

class ADDQuestionsView(CreateAPIView, ListAPIView):
    queryset = Question_tmp.objects.order_by('id')
    serializer_class = QuestionTMPSerializers
    permission_classes = (isManagementPermission,)

    def list(self, request, *args, **kwargs):
        qt_id = request.query_params.get("qt_id")
        queryset = Question_tmp.objects.filter(qt_id=qt_id)
        ser = self.get_serializer(queryset, many=True)
        return Response({"detail": "success", "result": ser.data})

    def create(self, request, *args, **kwargs):
        res = add_question(request)
        return Response({"detail": "success", "result": res})

class GetOptionView(APIView):
    permission_classes = (isManagementPermission,)
    def get(self, request):
        result = get_option_data(request)
        return Response({"detail": "success", "result": result})

class GetOptionsView(APIView):
    permission_classes = (isManagementPermission,)
    def get(self, request):
        result = get_question_option(request)
        return Response({"detail": "success", "result": result})

class ADDOrderAndValueView(CreateAPIView, ListAPIView):
    queryset = Option.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        add_order_and_select_value(request)
        return Response({"detail": "success"})

class ADDCalculateView(CreateAPIView, ListAPIView):
    queryset = Calculate_Exp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        add_calculate(request)
        return Response({"detail": "success"})

    def list(self, request, *args, **kwargs):
        result = get_calculate(request)
        return Response({"detail": "success", "result":result})

class ADDResultView(CreateAPIView, ListAPIView):
    queryset = Calculate_Exp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        add_result(request)
        return Response({"detail": "success"})

    def list(self, request, *args, **kwargs):
        result = get_add_result(request)
        return Response({"detail": "success", "result":result})

class ShowResultView(APIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def get(self, request, *args, **kwargs):
        result = show_result(request)
        return Response({"detail": "success", "result": result})


class GetquestionsView(ListAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def list(self, request, *args, **kwargs):
        qt_id = request.query_params.get("qt_id")
        query = self.get_queryset().filter(qt_id=qt_id)
        questions = []
        q_id_list = []
        for q in query:
            if q.q_attr == "普通题": # 将性别题和年龄题去除
                if q.q_type != "问答题":
                    questions.append({"number": q.number, "q_id": q.u_id})
                    q_id_list.append(q.u_id)
        ans = Option_tmp.objects.filter(q_id__in=q_id_list)
        an_set = set()
        value_list = []
        for an in ans:
            if an.value and an.value not in an_set and an.value != '\\':
                an_set.add(an.value)
                try:
                    float(an.value)
                except Exception as e:   # 不是数字的才加入统计计算的返回
                    value_list.append({"value": an.value, "value_cn": '{' + an.value + '}' + '的个数'})
        data = {"question_number": questions, "value_list": value_list}
        return Response({"detail": "success", "result": data})

class SubmitCheckView(CreateAPIView): # 提交审核
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        if obj:
            if obj.status_tmp == "草稿":
                obj.status_tmp = "待审核"
                obj.save()
                return Response({"detail": "success"})
            if obj.status_tmp =="已上线（有草稿）":
                obj.status_tmp = "已上线（草稿待审核）"
                obj.save()
                return Response({"detail": "success"})
            return Response({"detail": "非草稿无法提交审核！"}, status=400)
        return Response({"detail": "问卷不存在！"}, status=400)


class UndoCheckView(CreateAPIView): # 撤销审核
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        user = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        if obj:
            if user_is_operator(request):  # 如果是运营人员，判断是否有权限
                if obj.create_user != user:
                    return Response({"detail": "无权限操作！"}, status=403)
            if obj.status_tmp == "待审核":
                obj.status_tmp = "草稿"
                obj.save()
                return Response({"detail": "success"})
            if obj.status_tmp == "已上线（草稿待审核）":
                obj.status_tmp = "已上线（有草稿）"
                obj.save()
                return Response({"detail": "success"})
            return Response({"detail": "非待审核数据不支持撤销！"}, status=400)
        return Response({"detail": "问卷不存在！"}, status=400)

class SubmitCheckResultView(CreateAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (idAdminAndCheckerPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        status = data.get('status')
        obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        check_time = datetime.datetime.now()
        check_user = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        if not obj:
            return Response({"detail": "问卷不存在！"}, status=400)
        if obj.status_tmp not in ["待审核", "已上线（草稿待审核）"]:
            return Response({"detail": "非待审核数据不支持操作！"}, status=400)
        if status == "审核拒绝":
            t_status = "审核拒绝"
            if obj.status == "已上线（草稿待审核）":
                t_status = "已上线（草稿审核拒绝）"
            QuestionType_tmp.objects.filter(u_id=qt_id).update(status_tmp=t_status,
                                                               check_time=check_time, check_user=check_user)
            return Response({"detail": "success"})
        if status == "已上线":
            QuestionType_tmp.objects.filter(u_id=qt_id).update(status_tmp="已上线", status="已上线",
                                                               check_time=check_time, check_user=check_user)
            copy_tmp_table(qt_id)
            return Response({"detail": "success"})
        return Response({"detail": "参数错误！"}, status=400)

class OnlineResultView(CreateAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (idAdminAndCheckerPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        operator = data.get('operator')
        if operator == "启用": # 已下线->草稿
            obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
            if obj:
                if obj.status != "已下线":
                    return Response({"detail": "只能操作已下线问卷！"}, status=400)
                obj.status_tmp = "草稿"
                obj.status = "草稿"
                obj.save()
                # copy_tmp_table(qt_id)
                return Response({"detail": "success"})
            return Response({"detail": "问卷不存在！"}, status=400)
        if operator == "下线":  # 已上线->已下线
            obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
            if obj:
                if obj.status != "已上线":
                    return Response({"detail": "只能操作已上线问卷！"}, status=400)
                obj.status_tmp="已下线"
                obj.status="已下线"
                obj.save()
                # copy_tmp_table(qt_id)
                QuestionType.objects.filter(u_id=qt_id).update(status_tmp="已下线", status="已下线")
                return Response({"detail": "success"})
            return Response({"detail": "问卷不存在！"}, status=400)
        return Response({"detail": "参数错误！"}, status=400)

class DeleteView(CreateAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
        if not obj:
            return Response({"detail": "问卷不存在！"}, status=400)
        user = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        if user_is_operator(request):  # 如果是运营人员，判断是否有权限
            if obj.create_user != user:
                return Response({"detail": "无权限操作！"}, status=403)
        if obj.status_tmp not in ["草稿", "已上线（有草稿）"]:
            return Response({"detail": "只能删除草稿问卷！"}, status=400)
        if obj.status_tmp == "草稿":
            obj.delete()  # 草稿直接删除(还要删除关联数据)
        else:
            # 将已上线的表数据复制回来
            copy_use_table(qt_id)
        return Response({"detail": "success"})

class CopyAPIView(CreateAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        user = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        new_qt_id, title = copy_question(qt_id, user)
        return Response({"detail": "success", "data": {'title': title,"new_qt_id": new_qt_id}})

class IndexView(CreateAPIView):
    queryset = QuestionType_tmp.objects.all()
    serializer_class = QuestionTypeTMPListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        title = data.get('title')
        status_tmp = data.get('status_tmp')
        create_user = data.get('create_user')
        check_user = data.get('check_user')
        order = data.get('order')
        download = data.get('download')
        queryset = self.get_queryset()
        if title:
            queryset = queryset.filter(title__icontains=title)
        if create_user:
            queryset = queryset.filter(create_user__icontains=create_user)
        if check_user:
            queryset = queryset.filter(check_user__icontains=check_user)
        if status_tmp:
            queryset = queryset.filter(status_tmp__in=status_tmp)
        for o in order:
            order_list = ['show_number', '-show_number', "finish_number", "-finish_number",
                          "create_time", '-create_time', 'update_time', '-update_time']
            if o in order_list:
                queryset = queryset.order_by(o)
        if not order:
            queryset = queryset.order_by('-update_time')
        if download: # 下载
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CheckIndexView(CreateAPIView):
    queryset = QuestionType_tmp.objects.filter(status_tmp__in=["审核拒绝", "已上线", "待审核", "已上线（草稿待审核）", '已上线（有草稿）'])
    serializer_class = QuestionTypeTMPListSerializers
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)
    def create(self, request, *args, **kwargs):
        data = request.data
        title = data.get('title')
        update_user = data.get('update_user')
        status_tmp = data.get('status_tmp')
        order = data.get('order')
        download = data.get('download')
        queryset = self.get_queryset()
        if title:
            queryset = queryset.filter(title__icontains=title)
        if update_user:
            queryset = queryset.filter(update_user__icontains=update_user)
        if status_tmp:
            queryset = queryset.filter(status_tmp__in=status_tmp)
        for o in order:
            order_list = ['check_time', '-check_time',"create_time", '-create_time', 'update_time', '-update_time']
            if o in order_list:
                queryset = queryset.order_by(o)
        if not order:
            queryset = queryset.order_by('-update_time')
        if download: # 下载
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ShowquestionAPIView(ListAPIView):
    queryset = QuestionType_tmp.objects.order_by('id')
    permission_classes = (isManagementPermission,)

    def list(self, request, *args, **kwargs):
        qt_id = request.query_params.get("qt_id")
        result = get_show_question(qt_id)
        return Response({"detail": "success", "data": result})