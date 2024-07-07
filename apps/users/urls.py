from apps.users import views
from django.urls import path, re_path

urlpatterns = [
    path(r'register/', views.RegisterAPIView.as_view()),    # 后台注册
    path(r'login/', views.LoginAPIView.as_view()),          # 后台登录
    re_path(r'^userAudit/$', views.UserAuditAPIView.as_view()),  # 审核用户
    re_path(r'^upload/$', views.UploadMedioAPIView.as_view()),  # 上传音频生成二维码
    re_path(r'^qrcode/$', views.QRcodeurlView.as_view()),       # 返回二维码内容

]
