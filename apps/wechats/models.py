from django.db import models

# Create your models here.
from apps.questions.models import default_data

class UserAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷id")
    user_id = models.CharField(max_length=128, default='', verbose_name="答题人id")
    answer = models.JSONField(default=default_data, verbose_name="回答")
    result = models.JSONField(default=default_data, verbose_name="结果")
    is_finish = models.CharField(max_length=32, default="", verbose_name="是否完成")
    count_result = models.JSONField(default=default_data, verbose_name="结果统计")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_user_answer"

class UserAnswer_tmp(models.Model):
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷id")
    user_id = models.CharField(max_length=128, default='', verbose_name="答题人id")
    answer = models.JSONField(default=default_data, verbose_name="回答")
    result = models.JSONField(default=default_data, verbose_name="结果")
    is_finish = models.CharField(max_length=32, default="", verbose_name="是否完成")
    count_result = models.JSONField(default=default_data, verbose_name="结果统计")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_user_answer_tmp"

class UserShow_number(models.Model):
    id = models.AutoField(primary_key=True)
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷id")
    user_id = models.CharField(max_length=128, default='', verbose_name="答题人id")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_user_show"

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    user_id = models.CharField(max_length=128, default='', verbose_name="用户id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷id")
    title = models.CharField(max_length=128, default='', verbose_name="问卷标题")
    pay_status = models.CharField(max_length=128, default='', verbose_name="支付状态，待支付|已支付")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_order"


class Order_tmp(models.Model):
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    user_id = models.CharField(max_length=128, default='', verbose_name="用户id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷id")
    title = models.CharField(max_length=128, default='', verbose_name="问卷标题")
    pay_status = models.CharField(max_length=128, default='', verbose_name="支付状态，待支付|已支付")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_order_tmp"