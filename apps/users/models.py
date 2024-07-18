import datetime

from django.db import models


# Create your models here.

class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=64, default='', verbose_name="用户ID", unique=True)
    name = models.CharField(max_length=32, default='', verbose_name="用户名")
    user_name = models.CharField(max_length=32, default='', verbose_name="姓名")
    check_user = models.CharField(max_length=32, default='', verbose_name="审核人")
    mobile = models.CharField(max_length=32, default='', verbose_name="手机号码")
    email = models.CharField(max_length=32, default='', verbose_name="邮箱")
    password = models.CharField(max_length=64, default='', verbose_name="密码")
    status = models.CharField(max_length=32, default='used', verbose_name="用户状态") # used|checking待审核|pending待生效|deny已拒绝|已注销deleted
    role = models.IntegerField(default=0, verbose_name='管理员1|审核员2|运营人员3|其他用100')
    tag = models.IntegerField(default=0, verbose_name="是否立即生效")  # 1立即生效 | 0指定时间段生效
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="账号开始使用时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="账号结束使用时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    token = models.CharField(max_length=256, default='', verbose_name="token")
    token_exp = models.DateTimeField(auto_now=True, null=True, verbose_name='token 过期时间')

    class Meta:
        db_table = "user"


class Media(models.Model):
    id = models.AutoField(primary_key=True)
    file_id = models.CharField(max_length=64, default="", unique=True, verbose_name="文件id")
    title = models.CharField(max_length=64, default="", verbose_name="标题")
    name = models.CharField(max_length=64, default="", verbose_name="文件名称")
    type = models.CharField(max_length=32, default="", verbose_name="文件类型")
    path = models.CharField(max_length=64, default="", verbose_name="文件路径")
    time_limite = models.CharField(max_length=32, default="", verbose_name="使用限制")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="生效时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    desc = models.CharField(max_length=64, default="", verbose_name="描述信息")
    class Meta:
        db_table = "tong_media"



class CheckEmailCode(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=64, default="", verbose_name="邮箱")
    code = models.CharField(max_length=12, default="", verbose_name="验证码")
    time = models.DateTimeField(auto_now=True, null=True, verbose_name="创建时间")
    class Meta:
        db_table = "tong_check_code"


