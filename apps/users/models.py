import datetime

from django.db import models


# Create your models here.

class User(models.Model):
    user_id = models.CharField(max_length=64, default='', verbose_name="用户ID", unique=True)
    name = models.CharField(max_length=32, default='', verbose_name="用户名")
    mobile = models.CharField(max_length=32, default='', verbose_name="手机号码")
    password = models.CharField(max_length=64, default='', verbose_name="密码")
    status = models.CharField(max_length=32, default='used', verbose_name="用户状态")
    role = models.IntegerField(default=0, verbose_name='管理员1|审核员2|运营人员3|其他用100')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="账号开始使用时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="账号结束使用时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    token = models.CharField(max_length=256, default='', verbose_name="token")
    token_exp = models.DateTimeField(auto_now=True, null=True, verbose_name='token 过期时间')

    class Meta:
        db_table = "user"


class Media(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=64, default="", verbose_name="标题")
    type = models.CharField(max_length=32, default="", verbose_name="类型")
    name = models.CharField(max_length=64, default="", verbose_name="名称")
    time_limite = models.CharField(max_length=32, default="", verbose_name="使用限制")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="生效时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    desc = models.CharField(max_length=64, default="", verbose_name="描述信息")
    class Meta:
        db_table = "tong_media"


