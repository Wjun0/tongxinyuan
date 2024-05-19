from rest_framework import serializers

from apps.users.models import User


class UserSerizlizers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name', 'mobile', 'role', 'create_time', 'status')
