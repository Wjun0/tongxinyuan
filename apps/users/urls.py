from apps.users import views
from django.urls import path, re_path

urlpatterns = [
    re_path(r'^userLogin/$', views.LoginAPIView.as_view()),
    path(r'register/', views.RegisterAPIView.as_view()),
    re_path(r'^userAudit/$', views.UserAuditAPIView.as_view())

]
