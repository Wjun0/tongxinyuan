from rest_framework import serializers
from apps.questions.models import QuestionType, QuestionType_tmp


class QuestionTypeTMPListSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionType_tmp
        fields = "__all__"

class QuestionTypeTMPSerializers(serializers.ModelSerializer):

    class Meta:
        model = QuestionType_tmp
        fields = ['u_id', 'start_time', 'end_time', 'background_img', 'title_img', 'title', 'test_value',
                  'test_value_html' ,'q_number', 'test_time', 'use_count', 'source', 'status']


class QuestionSerializers(serializers.ModelSerializer):

    class Meta:
        model = QuestionType
        fields = ['qt_id', 'q_type', 'q_attr', 'q_title',
                  'number', 'q_check_role']

