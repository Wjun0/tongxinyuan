from rest_framework import serializers
from django.conf import settings
from apps.questions.models import QuestionType

class QuestionTypeListSerializers(serializers.ModelSerializer):
    background_img = serializers.SerializerMethodField(method_name="get_background_img")
    title_img = serializers.SerializerMethodField(method_name="get_title_img")

    def get_background_img(self, instance):
        background_img = instance.background_img
        if background_img:
            return settings.DOMAIN + "/media/image/" + background_img
        return ""

    def get_title_img(self, instance):
        title_img = instance.title_img
        if title_img:
            return settings.DOMAIN + "/media/image/" + title_img
        return ""

    class Meta:
        model = QuestionType
        fields = ['u_id', 'background_img', 'title_img', 'title', 'test_value',
                  'test_value_html', 'q_number', 'test_time', 'use_count', 'source', 'status']

