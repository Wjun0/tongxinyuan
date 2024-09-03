from django.urls import path, re_path

from apps.wechats import views

urlpatterns = [
    re_path(r'^login/$', views.LoginAPIView.as_view()),     # 登录
    re_path(r'^list/$', views.IndexView.as_view()),         # 频道列表
    re_path(r'^detail/$', views.DetailView.as_view()),      # 详情
    re_path(r'^get_question/$', views.GETQuestionView.as_view()),  # 获取问题和选项
    re_path(r'^answer/$', views.QuestionView.as_view()),       # 回答问题




]