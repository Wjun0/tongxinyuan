import uuid

from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.questions.filters import QuestionTypetmpFilter
from apps.questions.models import QuestionType, Question, Calculate_Exp, Option, QuestionType_tmp, Question_tmp, \
    Option_tmp
from apps.questions.serizlizers import QuestionSerializers, QuestionTypeTMPListSerializers, \
    QuestionTypeTMPSerializers
from apps.questions.services import add_question_type, add_question, add_order_and_select_value, \
    add_calculate, add_result, show_result, get_option_data, get_calculate, copy_tmp_table, get_question_option
from apps.questions.upload_image_service import upload
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import isManagementPermission, idAdminAndCheckerPermission
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
        if u_id: # 更新逻辑
            qt = QuestionType_tmp.objects.filter(u_id=u_id).first()
            if qt:
                if qt.status == "已上线":
                    status_tmp = "已上线（有草稿）"
                elif qt.status == "已暂停":
                    status_tmp = "已暂停（有草稿）"
                else:
                    status_tmp = "草稿"
                data['status_tmp'] = status_tmp
                data['update_user'] = u_name
                QuestionType_tmp.objects.update_or_create(u_id=u_id, defaults=data)
                return Response({"detail": "success"})
        # else: # 新增逻辑
        uid = str(uuid.uuid4())
        data['status'] = "无"
        data['status_tmp'] = "草稿"
        data['u_id'] = uid
        data['create_user'] = u_name
        data['update_user'] = u_name
        res = QuestionType_tmp.objects.create(**data)
        result = {"u_id":res.u_id, "background_img": res.background_img, "title": res.title}
        return Response({"detail": "success", "result": result})

class ADDQuestionsView(CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializers
    permission_classes = (isManagementPermission,)

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

class ADDOrderAndValueView(CreateAPIView):
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

class ADDResultView(CreateAPIView):
    queryset = Calculate_Exp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        add_result(request)
        return Response({"detail": "success"})

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
            questions.append({"number": q.number, "q_id": '#' + str(q.u_id)})
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
                    value_list.append({"value": '{' + an.value + '}', "value_cn": '{' + an.value + '}' + '的个数'})
        data = {"question_number": questions, "value_list": value_list}
        return Response({"detail": "success", "result": data})

class SubmitCheckView(CreateAPIView): # 提交审核
    queryset = Question_tmp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        QuestionType_tmp.objects.filter(u_id=qt_id).update(status_tmp="审核中")
        return Response({"detail": "success"})

class SubmitCheckResultView(CreateAPIView):
    queryset = Question_tmp.objects.all()
    permission_classes = (idAdminAndCheckerPermission,)

    def create(self, request, *args, **kwargs):
        data = request.data
        qt_id = data.get('qt_id')
        status = data.get('status')
        if status == "已拒绝":
            QuestionType_tmp.objects.filter(u_id=qt_id).update(status_tmp="已拒绝")
        if status == "已生效":
            obj = QuestionType_tmp.objects.filter(u_id=qt_id).first()
            now = timezone.now()
            if obj.start_time < now < obj.end_time:
                obj.status = "已上线"
                obj.status_tmp = "已上线"
                obj.save()
                # 将tmp表导入到正式表
                copy_tmp_table(qt_id)
                return Response({"detail": "success"})
            QuestionType_tmp.objects.filter(u_id=qt_id).update(status_tmp="待生效")
        return Response({"detail": "success"})

class IndexView(ListAPIView):
    queryset = QuestionType_tmp.objects.order_by('-update_time')
    serializer_class = QuestionTypeTMPListSerializers
    filterset_class = QuestionTypetmpFilter
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)


