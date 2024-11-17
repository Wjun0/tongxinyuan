from django.urls import path, re_path

from apps.wechats import views, views_pay

urlpatterns = [
    re_path(r'^login/$', views.LoginAPIView.as_view()),     # 登录
    re_path(r'^get_phone/$', views.GetPhoneAPIView.as_view()),   # 获取手机号
    re_path(r'^user_info/$', views.UserInfoAPIView.as_view()),   # 用户信息
    re_path(r'^change_user_name/$', views.ChangeUsernameAPIView.as_view()),   # 修改用户名
    re_path(r'^change_phone/$', views.ChangePhoneAPIView.as_view()),          # 修改手机号
    re_path(r'^list/$', views.IndexView.as_view()),         # 频道列表
    re_path(r'^detail/$', views.DetailView.as_view()),      # 详情
    re_path(r'^get_question/$', views.GETQuestionView.as_view()),  # 获取问题和选项
    re_path(r'^answer/$', views.QuestionView.as_view()),       # 回答问题
    re_path(r'^result/$', views.ResultView.as_view()),         # 获取结果

    re_path(r'^pay/jsapi/$', views_pay.PayJsApiView.as_view()),     # 生成订单
    re_path(r'^notify/$', views_pay.NotifyView.as_view()),          # 回调函数
    re_path(r'^pay/query/$', views_pay.PayQueryView.as_view()),       # 查询订单状态

    re_path(r'^channel/$', views.ChannelAPIView.as_view()),       # 频道
    re_path(r'^upload/$', views.UploadView.as_view()),    # 上传音视频





]