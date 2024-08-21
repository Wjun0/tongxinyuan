from django.db import models

def default_data():
    return {}

class QuestionType(models.Model):
    # 问卷类型表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    background_img = models.CharField(max_length=128, null=True, blank=True, default='', verbose_name="问卷背景")
    title_img = models.CharField(max_length=128, default='', verbose_name="主图")
    title = models.CharField(max_length=32, default='', verbose_name="问卷标题")
    test_value = models.TextField(default='', verbose_name="测试价值")
    test_value_html = models.TextField(default='', verbose_name="测试价值 富文本")
    q_number = models.CharField(max_length=32, default=0, verbose_name="问题个数")
    test_time = models.CharField(max_length=32, default='', verbose_name="预计测试时间")
    use_count = models.IntegerField(default=0, verbose_name="已参与人数")
    source = models.CharField(max_length=255, default='', verbose_name="量表出处")
    status = models.CharField(max_length=32, default='', verbose_name="状态 草稿|使用中")
    status_tmp = models.CharField(max_length=32, default='', verbose_name="有无草稿 无|有草稿")
    show_number = models.CharField(max_length=32, default='', verbose_name="曝光数")
    finish_number = models.CharField(max_length=32, default='', verbose_name="完成人数")
    update_user = models.CharField(max_length=32, default='', verbose_name="最近更新人")
    create_user = models.CharField(max_length=32, default='', verbose_name="创建人")
    check_user = models.CharField(max_length=32, default='', verbose_name="审核人")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="问卷开始使用时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="问卷结束使用时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_question_type"

class QuestionType_tmp(models.Model):
    # 问卷类型表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='',unique=True, verbose_name="唯一id")
    background_img = models.CharField(max_length=128, null=True, blank=True, default='', verbose_name="问卷背景")
    title_img = models.CharField(max_length=128, default='', verbose_name="主图")
    title = models.CharField(max_length=32, default='', verbose_name="问卷标题")
    test_value = models.TextField(default='', verbose_name="测试价值")
    test_value_html = models.TextField(default='', verbose_name="测试价值 富文本")
    q_number = models.CharField(max_length=32, default=0, verbose_name="问题个数")
    test_time = models.CharField(max_length=32, default='', verbose_name="预计测试时间")
    use_count = models.IntegerField(default=0, verbose_name="已参与人数")
    source = models.CharField(max_length=255, default='', verbose_name="量表出处")
    status = models.CharField(max_length=32, default='', verbose_name="状态 草稿|使用中")
    status_tmp = models.CharField(max_length=32, default='', verbose_name="有无草稿 无|有草稿")
    show_number = models.CharField(max_length=32, default='', verbose_name="曝光数")
    finish_number = models.CharField(max_length=32, default='', verbose_name="完成人数")
    update_user = models.CharField(max_length=32, default='', verbose_name="最近更新人")
    create_user = models.CharField(max_length=32, default='', verbose_name="创建人")
    check_user = models.CharField(max_length=32, default='', verbose_name="审核人")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="问卷开始使用时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="问卷结束使用时间")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_question_type_tmp"

class Question(models.Model):
    # 问题表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    q_type = models.CharField(max_length=128, default='', verbose_name="问卷类型 单选|多选|简答")
    q_attr = models.CharField(max_length=128, default='', verbose_name="问卷属性 普通题|性别题|年龄题")
    q_value_type = models.CharField(max_length=128, default='', verbose_name="问卷赋值类型 分值|专制|D")
    q_title = models.TextField(default='', verbose_name="问卷标题")
    q_title_html = models.TextField(default='', verbose_name="问卷标题")
    number = models.CharField(max_length=128, default='', verbose_name="题目序号 问题1|问题2")  # 后面根据序号答题
    q_check_role = models.CharField(max_length=128, default='', verbose_name="校验规则 无|性别|年龄")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_question"

class Question_tmp(models.Model):
    # 问题表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    q_type = models.CharField(max_length=128, default='', verbose_name="问卷类型 单选|多选|简答")
    q_attr = models.CharField(max_length=128, default='', verbose_name="问卷属性 普通题|性别题|年龄题")
    q_value_type = models.CharField(max_length=128, default='', verbose_name="问卷赋值类型 分值|专制|D")
    q_title = models.TextField(default='', verbose_name="问卷标题")
    q_title_html = models.TextField(default='', verbose_name="问卷标题")
    number = models.CharField(max_length=128, default='', verbose_name="题目序号 问题1|问题2")  # 后面根据序号答题
    q_check_role = models.CharField(max_length=128, default='', verbose_name="校验规则 无|性别|年龄")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_question_tmp"

class Option(models.Model):
    # 选项表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    q_id = models.CharField(max_length=128, default='', verbose_name="题目id")
    o_number = models.CharField(max_length=32, default='', verbose_name="A|B|C|D|E|F选项")
    o_content = models.TextField(default='', verbose_name="选项描述")
    o_html_content = models.TextField(default='', verbose_name="选项描述富文本")
    next_q_id = models.IntegerField(default=0, verbose_name="下一题序号")  # 顺序时，下一题为0
    value = models.CharField(max_length=32, default='', verbose_name="分值或类型")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_option"
        unique_together = [['u_id', 'o_number']]

class Option_tmp(models.Model):
    # 选项表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    q_id = models.CharField(max_length=128, default='', verbose_name="题目id")
    o_number = models.CharField(max_length=32, default='', verbose_name="A|B|C|D|E|F选项")
    o_content = models.TextField(default='', verbose_name="选项描述")
    o_html_content = models.TextField(default='', verbose_name="选项描述富文本")
    next_q_id = models.IntegerField(default=0, verbose_name="下一题序号")  # 顺序时，下一题为0
    value = models.CharField(max_length=32, default='', verbose_name="分值或类型")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_option_tmp"
        unique_together = [['u_id', 'o_number']]

class Calculate_Exp(models.Model):
    # 计算因子表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    exp_name = models.CharField(max_length=128, default='', verbose_name="因子名称")
    exp_type = models.CharField(max_length=128, default='', verbose_name="因子类型 数字|文本|字母")
    exp = models.CharField(max_length=128, default='', verbose_name="表达式")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_calculate_exp"

class Calculate_Exp_tmp(models.Model):
    # 计算因子表
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    exp_name = models.CharField(max_length=128, default='', verbose_name="因子名称")
    exp_type = models.CharField(max_length=128, default='', verbose_name="因子类型 数字|文本|字母")
    exp = models.TextField(default='', verbose_name="表达式")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_calculate_exp_tmp"

class Result_Title(models.Model):
    # 结果
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    background_img = models.CharField(max_length=128, default='', verbose_name="结果背景")
    statement = models.CharField(max_length=512, default='', verbose_name="免责声明")
    result_img = models.CharField(max_length=128, default='', verbose_name="结果主图")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_result_title"

class Result_Title_tmp(models.Model):
    # 结果
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    background_img = models.CharField(max_length=128, default='', verbose_name="结果背景")
    statement = models.CharField(max_length=512, default='', verbose_name="免责声明")
    result_img = models.CharField(max_length=128, default='', verbose_name="结果主图")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')

    class Meta:
        db_table = "tong_result_title_tmp"

class Dimension(models.Model):
    # 维度名称，一条数据一个结果
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    r_id = models.CharField(max_length=128, default='', verbose_name="结果标题id")
    dimension_number = models.CharField(max_length=512, default='', verbose_name="维度序号")
    dimension_name = models.CharField(max_length=512, default='', verbose_name="维度名称")
    result_number = models.CharField(max_length=512, default='', verbose_name="结果序号")
    result_name = models.TextField(default='', verbose_name="结果名称")
    result_name_html = models.TextField(default='', verbose_name="结果名称")
    result_desc = models.TextField(default='', verbose_name="结果描述")
    result_desc_html = models.TextField(default='', verbose_name="结果描述")
    value = models.JSONField(default=default_data, verbose_name="赋值计算")
    # order_dic = {"value1": {"role": "校验规则", "exp_id": "计算因子", "format": "大于等于", "value": "比较值",
    #                 "min_age": 23, "max_age": 50, "sex":"男", "link": "且"},
    #      "value2": {"role": "校验规则", "exp_id": "计算因子", "format": "大于等于", "value": "比较值",
    #                 "min_age": 23, "max_age": 50, "sex": "男", "link": "且"}
    #      }
    class Meta:
        db_table = "tong_dimension"

class Dimension_tmp(models.Model):
    # 维度名称，一条数据一个结果
    id = models.AutoField(primary_key=True)
    u_id = models.CharField(max_length=128, default='', unique=True, verbose_name="唯一id")
    qt_id = models.CharField(max_length=128, default='', verbose_name="问卷类型id")
    r_id = models.CharField(max_length=128, default='', verbose_name="结果标题id")
    dimension_number = models.CharField(max_length=512, default='', verbose_name="维度序号")
    dimension_name = models.CharField(max_length=512, default='', verbose_name="维度名称")
    result_number = models.CharField(max_length=512, default='', verbose_name="结果序号")
    result_name = models.TextField(default='', verbose_name="结果名称")
    result_name_html = models.TextField(default='', verbose_name="结果名称")
    result_desc = models.TextField(default='', verbose_name="结果描述")
    result_desc_html = models.TextField(default='', verbose_name="结果描述")
    value = models.JSONField(default=default_data, verbose_name="赋值计算")
    # order_dic = {"value1": {"role": "校验规则", "exp_id": "计算因子", "format": "大于等于", "value": "比较值",
    #                 "min_age": 23, "max_age": 50, "sex":"男", "link": "且"},
    #      "value2": {"role": "校验规则", "exp_id": "计算因子", "format": "大于等于", "value": "比较值",
    #                 "min_age": 23, "max_age": 50, "sex": "男", "link": "且"}
    #      }
    class Meta:
        db_table = "tong_dimension_tmp"

class Image(models.Model):
    id = models.AutoField(primary_key=True)
    file_id = models.CharField(max_length=128, default='', verbose_name="文件id")
    file_name = models.CharField(max_length=128, default='', verbose_name="文件名称")
    source = models.CharField(max_length=128, default='', verbose_name="来源")

    class Meta:
        db_table = "tong_image"








