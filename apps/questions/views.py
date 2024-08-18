from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response

from apps.questions.filters import QuestionTypeFilter
from apps.questions.models import QuestionType, Question
from apps.questions.serizlizers import QuestionTypeSerializers, QuestionSerializers
from apps.questions.services import add_question_type, add_question
from apps.questions.upload_image_service import upload
from apps.users.pagenation import ResultsSetPagination
from apps.users.permission import isManagementPermission

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
        data = request.data
        data['status'] = "草稿"
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "success", "result": serializer.data})

class ADDQuestionsView(CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializers
    permission_classes = (isManagementPermission,)

    def create(self, request, *args, **kwargs):
        res = add_question(request)
        return Response({"detail": "success", "result": res})


class IndexView(ListAPIView):
    queryset = QuestionType.objects.order_by('-update_time')
    serializer_class = QuestionTypeSerializers
    filterset_class = QuestionTypeFilter
    pagination_class = ResultsSetPagination
    permission_classes = (isManagementPermission,)


