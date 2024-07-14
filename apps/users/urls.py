from apps.users import views
from django.urls import path, re_path

urlpatterns = [
    re_path(r'register/$', views.RegisterAPIView.as_view()),    # 后台注册
    re_path(r'userAdd/$', views.UserAddAPIView.as_view()),      # 添加用
    re_path(r'login/$', views.LoginAPIView.as_view()),          # 后台登录
    re_path(r'userList/$', views.UserAPIView.as_view()),       # 用户列表
    re_path(r'^userAudit/$', views.UserAuditAPIView.as_view()),  # 审核用户
    re_path(r'^upload/$', views.UploadMedioAPIView.as_view()),  # 上传音频生成二维码
    path('download/<file_name>/', views.QRcodeurlView.as_view()),       # 返回二维码内容
    re_path(r'^mediaList/$', views.MediaListAPIView.as_view()),       # 返回上传文件列表
    re_path(r'^userPermission/$', views.UserPermissionAPIView.as_view()),  # 返回用户权限信息
    re_path(r'^checkUser/$', views.ChechUserAPIView.as_view()),              # 检查用户名是否被占用


]
