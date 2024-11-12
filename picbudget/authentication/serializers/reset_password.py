# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value
