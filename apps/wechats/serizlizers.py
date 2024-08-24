from rest_framework import serializers

from apps.questions.models import QuestionType

class QuestionTypeListSerializers(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = "__all__"

