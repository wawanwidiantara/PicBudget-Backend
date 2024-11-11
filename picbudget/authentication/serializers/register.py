from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user and user.status == "verified":
            raise ValidationError(
                "A user with this email already exists and is verified."
            )
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        password = validated_data["password"]
        user, created = User.objects.get_or_create(email=email)
        if created or user.status == "unverified":
            user.set_password(password)
            user.status = "unverified"
            user.save()
        return user
