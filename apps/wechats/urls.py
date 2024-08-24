from django.urls import path, re_path

from apps.wechats import views

urlpatterns = [
    re_path(r'^list/$', views.IndexView.as_view()),  # 频道列表
    re_path(r'^detail/$', views.IndexView.as_view()),  # 详情
    re_path(r'^anwser/$', views.AnswerView.as_view()),  # 答题


]