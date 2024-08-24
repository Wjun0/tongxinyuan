from rest_framework import serializers
from apps.questions.models import QuestionType, QuestionType_tmp


class QuestionTypeTMPListSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionType_tmp
        fields = "__all__"

class QuestionTypeSerializers(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = QuestionType
        fields = ["id",'background_img', 'title_img', 'title', 'test_value',
                  'q_number', 'test_time', 'use_count', 'source',
                  'status', 'start_time', 'end_time']
        extra_kwargs = {
            'background_img': {'allow_null': True}
        }

class QuestionSerializers(serializers.ModelSerializer):

    class Meta:
        model = QuestionType
        fields = ['qt_id', 'q_type', 'q_attr', 'q_title',
                  'number', 'q_check_role']

