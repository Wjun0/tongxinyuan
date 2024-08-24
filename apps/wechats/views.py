from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView, CreateAPIView

from apps.questions.models import QuestionType, Question
from apps.users.pagenation import ResultsSetPagination
from apps.wechats.serizlizers import QuestionTypeListSerializers


class IndexView(ListAPIView):
    queryset = QuestionType.objects.order_by('-update_time')
    serializer_class = QuestionTypeListSerializers
    # filterset_class = QuestionTypeFilter
    pagination_class = ResultsSetPagination
    # permission_classes = (isManagementPermission,)

class AnswerView(CreateAPIView):

    def create(self, request, *args, **kwargs):
        data = request
        qt_id = data.get('qt_id')
        last_q_id = data.get('last_q_id')
        last_answer = data.get('last_answer')
        if not last_q_id and not last_answer:
            # 获取第一题
            obj = Question.objects.filter(qt_id=qt_id, number="1").first()
            if not obj:
                return
            result = {"q_id": obj.q_id, }