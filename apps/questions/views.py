import uuid

from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response

from apps.questions.filters import QuestionTypeFilter
from apps.questions.models import QuestionType, Question, Calculate_Exp, Answer, QuestionType_tmp, Question_tmp
from apps.questions.serizlizers import QuestionTypeSerializers, QuestionSerializers, QuestionTypeListSerializers
from apps.questions.services import add_question_type, add_question, add_order_and_select_value, \
    add_calculate
from apps.questions.upload_image_service import upload
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import isManagementPermission
from apps.users.utils import token_to_name


class UploadImage(CreateAPIView):
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        file_id, file_name = upload(request)
        return Response({"file_id": file_id, "file_name": file_name})

class ADDQuestionsTypeView(CreateAPIView):
    queryset =  QuestionType.objects.all()
    serializer_class = QuestionTypeSerializers
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        if not add_question_type(request):
            return Response({"detail": "参数错误！"}, status=400)
        u_name = token_to_name(request.META.get('HTTP_AUTHORIZATION'))
        uid = str(uuid.uuid4())
        data = request.data
        data['status'] = "草稿"
        data['status_tmp'] = "无"
        data['u_id'] = uid
        data['create_user'] = u_name
        QuestionType_tmp.objects.create(**data)
        res = QuestionType.objects.create(**data)
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        result = {"u_id":res.u_id, "background_img": res.background_img, "title": res.title}
        return Response({"detail": "success", "result": result})

class ADDQuestionsView(CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializers
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        res = add_question(request)
        return Response({"detail": "success", "result": res})

class ADDOrderAndValueView(CreateAPIView):
    queryset = Answer.objects.all()
    permission_classes = (isManagementPermission,)
    def create(self, request, *args, **kwargs):
        add_order_and_select_value(request)
        return Response({"detail": "success"})

class ADDCalculateView(CreateAPIView):
    queryset = Calculate_Exp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        add_calculate(request)
        return Response({"detail": "success"})

class ADDResultView(CreateAPIView):
    queryset = Calculate_Exp.objects.all()
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):

        return Response({"detail": "success 开发中"})


class GetquestionsView(ListAPIView):
    queryset = Question_tmp.objects.all()
    # permission_classes = (isManagementPermission,)

    def list(self, request, *args, **kwargs):
        qt_id = request.query_params.get("qt_id")
        query = self.get_queryset().filter(qt_id=qt_id)
        questions = []
        q_id_list = []
        for q in query:
            questions.append({"number": q.number, "value": '#' + str(q.id)})
            q_id_list.append(q.id)
        ans = Answer.objects.filter(q_id__in=q_id_list)
        an_set = set()
        value_list = []
        for an in ans:
            if an.value not in an_set and an.value != '\\':
                an_set.add(an.value)
                try:
                    float(an.value)
                except Exception as e:   # 不是数字的才加入统计计算的返回
                    value_list.append({"value": '{' + an.value + '}', "value_cn": '{' + an.value + '}' + '的个数'})
        data = {"question_number": questions, "value_list": value_list}
        return Response({"detail": "success", "result": data})


class IndexView(ListAPIView):
    queryset = QuestionType.objects.order_by('-update_time')
    serializer_class = QuestionTypeListSerializers
    filterset_class = QuestionTypeFilter
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)


