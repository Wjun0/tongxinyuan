from django_filters import rest_framework
from apps.questions.models import QuestionType, QuestionType_tmp


class QuestionTypetmpFilter(rest_framework.FilterSet):

    class Meta:
        model = QuestionType_tmp
        fields = ["title", "status", "create_time"]