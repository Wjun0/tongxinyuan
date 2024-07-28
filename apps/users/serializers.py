import os

from django.conf import settings
from rest_framework import serializers
from apps.users.models import User, Media


class UserSerizlizers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('user_id', 'name', "user_name", 'check_user', 'email', 'role', 'create_time', 'status')

class MedaiSerializers(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField(method_name="get_user_id")

    def get_url(self, instance):
        return settings.DOMAIN + "/user/download/" + instance.file_id

    def get_user_id(self, instance):
        user = User.objects.filter(name=instance.user).first()
        return user.user_id if user else ""

    class Meta:
        model = Media
        fields = '__all__'