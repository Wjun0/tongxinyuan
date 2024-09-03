from django_filters import rest_framework
from apps.questions.models import QuestionType, QuestionType_tmp


class QuestionTypetmpFilter(rest_framework.FilterSet):
    title = rest_framework.CharFilter(method="title_filter")

    def title_filter(self, queryset, key, value):
        return queryset.filter(title__icontains=value)

    class Meta:
        model = QuestionType_tmp
        fields = ["title", "status", "create_user", "check_user"]