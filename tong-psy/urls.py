"""
URL configuration for tong-psy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import datetime

from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from django.urls import re_path
from django.views import static ##新增
from django.conf import settings ##新增
from rest_framework.permissions import BasePermission
from apps.questions.views import UploadImage


class MyOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        for path in schema['paths']:
            if "patch" in schema['paths'][path]:
                schema['paths'][path].pop("patch")
        return schema


class APIPermission(BasePermission):
    def has_permission(self, request, view):
        print(request.data)
        return True


schema_view = get_schema_view(
    # API 信息
    openapi.Info(
        title='接口文档',   # API文档标题
        default_version='V1',   # 版本信息
        description='接口文档',    # 描述内容
        # terms_of_service='https://qaq.com',    # 开发团队地址
        # contact=openapi.Contact(email='https://qaq.@qq.com',url='https://qaq.com'),   # 联系人信息：邮件、网址
        # license=openapi.License(name='qaq License'),    # 证书
    ),
    public=True,    # 是否公开
    # permission_classes=(APIPermission,),   # 设置用户权限
    generator_class=MyOpenAPISchemaGenerator,   # 自定义方法，去除patch方法的文档
)

# ==================更正数据===============
#from apps.users.tests import update_table
# update_table()
# ========================================


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.schedule_utils import update_user_status, update_question_status, backup_data

sche = BackgroundScheduler()
sche.add_job(update_user_status, trigger=CronTrigger(second="*/30"), max_instances=2)  # 30秒执行一次
sche.add_job(backup_data, trigger=CronTrigger(hour=1), max_instances=2)  # 30秒执行一次
# sche.add_job(update_question_status, trigger=CronTrigger(second="*/30"), max_instances=2)  # 更新问卷状态
sche.start()

urlpatterns = [
    #path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),  # 前端静态资源
    re_path(r'^media/image/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}, name='image'),  # 问卷图片
    #path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),   # 互动模式
    #path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),   # 文档模式
    re_path(r'^upload_img/', UploadImage.as_view()),
    path('user/', include('apps.users.urls')),
    path('question/', include('apps.questions.urls')),
    path('wechat/v1/', include('apps.wechats.urls')),
]


