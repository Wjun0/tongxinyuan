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
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.urls import re_path
from django.views import static ##新增
from django.conf import settings ##新增


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
    # public=True,    # 是否公开
    permission_classes=(permissions.AllowAny,)   # 设置用户权限

)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),   # 互动模式
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),   # 文档模式
    path('auth/', include('apps.users.urls')),
]

print(urlpatterns)

