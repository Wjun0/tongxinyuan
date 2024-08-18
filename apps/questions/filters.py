from django_filters import rest_framework
from apps.questions.models import QuestionType

class QuestionTypeFilter(rest_framework.FilterSet):

    class Meta:
        model = QuestionType
        fields = ["title", "status", "create_time"]