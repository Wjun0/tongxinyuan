from apps.users import views, strem_view, upload_view, upload_view_class
from django.urls import path, re_path

urlpatterns = [
    re_path(r'register/$', views.RegisterAPIView.as_view()),    # 后台注册
    re_path(r'userAdd/$', views.UserAddAPIView.as_view()),      # 添加用
    re_path(r'login/$', views.LoginAPIView.as_view()),          # 后台登录
    re_path(r'logout/$', views.LogoutAPIView.as_view()),         # 退出
    re_path(r'reflush/$', views.ReflushAPIView.as_view()),        # 刷新token
    re_path(r'forgetPwd/$', views.ForgetPdAPIView.as_view()),    # 忘记密码
    re_path(r'changePwd/$', views.ChangePdAPIView.as_view()),    # 修改密码
    re_path(r'userList/$', views.UserAPIView.as_view()),          # 用户列表
    re_path(r'^userAudit/$', views.UserAuditAPIView.as_view()),     # 审核用户

    re_path(r'^index/$', upload_view_class.IndexUploadView.as_view()),  # 一个分片上传后被调用
    re_path(r'^success/$', upload_view_class.SuccessUploadView.as_view()),  # 所有分片上传成功后被调用

    re_path(r'^upload/$', views.UploadMedioAPIView.as_view()),      # 上传音频生成二维码
    re_path(r'^upload_url/$', views.UploadUrlMedioAPIView.as_view()),      # 上传链接生成二维码
    re_path(r'^uploadLogo/$', views.UploadLogoAPIView.as_view()),      # 上传封面
    re_path(r'^uploadQRcode/$', views.UploadQRcodeAPIView.as_view()),      # 上传二维码
    #path('download/<file_id>/', views.QRcodeurlView.as_view()),       # 下载音频|视频
    path('download/<file_id>', strem_view.play_media),               # url播放
    path('play/<file_id>', strem_view.stream_video_m3u8),            # 前端播放 m3u8/ts

    path('get_m3u8/', views.GetM3u8View.as_view()),                  # file_id 换取m3u8
    path('download_user_m3u8/<file_id>', views.M3u8View.as_view()),  # 下载播放用户回答的问题 m3u8/ts
    path('download_user_media/<file_id>', views.DownloadUserMedia.as_view()),  # 下载文件 range

    path('PCdownload/<file_id>', views.PCstream_video_View.as_view()),            # 前端播放二维码音视频
    path('download_logo/<logo_id>/', views.DownloadLogoView.as_view()),    # 下载logo
    path('download_qrcode/<qrcode_id>/', views.DownloadQrcodeView.as_view()),    # 下载二维码
    re_path(r'^mediaList/$', views.MediaListAPIView.as_view()),             # 返回上传文件列表
    re_path(r'^mediaDetail/$', views.MediaDetailAPIView.as_view()),         # 文件详情
    re_path(r'^mediaDelete/$', views.MediaDeleteAPIView.as_view()),         # 单独的删除接口
    re_path(r'^userPermission/$', views.UserPermissionAPIView.as_view()),  # 返回用户权限信息
    re_path(r'^checkUser/$', views.ChechUserAPIView.as_view()),              # 检查用户名是否被占用
    re_path(r'^checkEmail/$', views.ChechEmailAPIView.as_view()),            # 检查邮箱否被占用
    re_path(r'^send_email/$', views.SendEmailAPIView.as_view()),             # 发送邮件
    re_path(r'^userInfo/$', views.UserInfoAPIView.as_view()),                 # 用户信息
    re_path(r'^wexin_userInfo/$', views.WeixinUserInfoAPIView.as_view()),     # 微信用户回答信息
    re_path(r'^wexin_userdetail/$', views.WeixinUserDetailAPIView.as_view()), # 微信用户回答详情
    re_path(r'^checkpwd/$', views.CheckPWDandEmailView.as_view()),           # 校验密码和邮箱



    # path('index/', upload_view.index),  # 一个分片上传后被调用
    # path('success/', upload_view.upload_success),  # 所有分片上传成功后被调用
    # path('file_exist/', upload_view.list_exist),  # 判断文件的分片是否存在
]
