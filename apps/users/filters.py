from django.conf import settings
from django_filters import rest_framework
from apps.users.models import User, Media
from apps.wechats.models import UserAnswer


class UserListerFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(method="name_filter")
    user_name = rest_framework.CharFilter(method="user_name_filter")
    role = rest_framework.CharFilter(method="role_filter")
    status = rest_framework.CharFilter(method="status_filter")

    def name_filter(self, queryset, key, value):
        return queryset.filter(name__icontains=value)

    def user_name_filter(self, queryset, key, value):
        return queryset.filter(user_name__icontains=value)

    def role_filter(self, queryset, key, value):
        return queryset.filter(role__in=value)

    def status_filter(self, queryset, key, value):
        return queryset.filter(status__in=value)


    class Meta:
        model = User
        fields = ["name", "user_name", "role", "status"]


class MediaListerFilter(rest_framework.FilterSet):
    start_time = rest_framework.CharFilter(method="start_time_filter")
    end_time = rest_framework.CharFilter(method="end_time_filter")
    url = rest_framework.CharFilter(method="url_filter")

    def start_time_filter(self, queryset, key, value):
        return queryset.filter(create_time__gte=value)

    def end_time_filter(self, queryset, key, value):
        return queryset.filter(create_time__lte=value)

    def url_filter(self, queryset, key, value):
        file_id = value.replace(settings.DOMAIN, "").replace("user/download/", "").replace("/","")
        return queryset.filter(file_id=file_id)

    class Meta:
        model = Media
        fields = ["user", "type", "start_time", "end_time", "url"]

class UserAnswerMediaListerFilter(rest_framework.FilterSet):

    def start_time_filter(self, queryset, key, value):
        return queryset.filter(create_time__gte=value)

    def end_time_filter(self, queryset, key, value):
        return queryset.filter(create_time__lte=value)
    #
    # def url_filter(self, queryset, key, value):
    #     file_id = value.replace(settings.DOMAIN, "").replace("user/download/", "").replace("/","")
    #     return queryset.filter(file_id=file_id)

    class Meta:
        model = UserAnswer
        fields = ["create_time", "update_time"]
