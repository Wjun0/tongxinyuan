from rest_framework import serializers
from apps.questions.models import QuestionType, QuestionType_tmp, Option_tmp, Question_tmp, Channel_tmp
from apps.users.models import User


class QuestionTypeTMPListSerializers(serializers.ModelSerializer):
    create_user_id = serializers.SerializerMethodField(method_name="get_create_user_id")
    class Meta:
        model = QuestionType_tmp
        fields = ['u_id', 'title', 'show_number', 'finish_number', 'create_time', 'update_time', 'qt_type',
                  'create_user', 'create_user_id', 'check_user', 'update_user', 'status_tmp', 'check_time']

    def get_create_user_id(self, instance):
        user = User.objects.filter(name=instance.create_user).first()
        return user.user_id if user else ""

class QuestionTypeTMPSerializers(serializers.ModelSerializer):

    class Meta:
        model = QuestionType_tmp
        fields = ['u_id', 'start_time', 'end_time', 'background_img', 'title_img', 'title', 'test_value',
                  'test_value_html' ,'q_number', 'test_time', 'use_count', 'source', 'status', 'amount',
                  'pay_type']

class QuestionTMPSerializers(serializers.ModelSerializer):
    q_options = serializers.SerializerMethodField(method_name="get_q_options")
    # 添加问题的序列化
    class Meta:
        model = Question_tmp
        fields = ['u_id', 'qt_id', 'q_type', 'q_attr', 'q_value_type', 'q_title', 'q_title_html',
                  'number', 'q_check_role', 'min_age', 'max_age', 'sex', 'q_options']

    def get_q_options(self, instance):
        ops = []
        objs = Option_tmp.objects.filter(q_id=instance.u_id)
        for i in objs:
            data = {'u_id': i.u_id, 'q_id': i.q_id, 'o_number': i.o_number, 'o_content':i.o_content,
                    'o_html_content': i.o_html_content, 'next_q_id': i.next_q_id, 'value':i.value}
            ops.append(data)
        return ops

class Channel_tmpListSerializers(serializers.ModelSerializer):
    class Meta:
        model = Channel_tmp
        fields = ['u_id', 'main_title', 'type', 'update_user', 'create_user', 'check_user', 'create_time', 'update_time', 'status']