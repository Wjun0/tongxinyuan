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

    def get_url(self, instance):
        return settings.DOMAIN + "user/download/" + instance.file_id

    class Meta:
        model = Media
        fields = '__all__'