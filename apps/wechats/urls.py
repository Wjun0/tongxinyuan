from django.urls import path, re_path

from apps.wechats import views, views_pay

urlpatterns = [
    re_path(r'^login/$', views.LoginAPIView.as_view()),     # 登录
    re_path(r'^get_phone/$', views.GetPhoneAPIView.as_view()),   # 获取手机号
    re_path(r'^list/$', views.IndexView.as_view()),         # 频道列表
    re_path(r'^detail/$', views.DetailView.as_view()),      # 详情
    re_path(r'^get_question/$', views.GETQuestionView.as_view()),  # 获取问题和选项
    re_path(r'^answer/$', views.QuestionView.as_view()),       # 回答问题
    re_path(r'^result/$', views.ResultView.as_view()),         # 获取结果

    re_path(r'^pay/jsapi/$', views_pay.PayJsApiView.as_view()),     # 生成订单
    re_path(r'^notify/$', views_pay.NotifyView.as_view()),          # 回调函数
    re_path(r'^pay/query/$', views_pay.PayQueryView.as_view())       # 查询订单状态



]