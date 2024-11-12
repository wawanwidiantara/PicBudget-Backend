from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")

            if user.status != "verified":
                msg = _(
                    "User account is not verified. Please verify your account first."
                )
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)

        update_last_login(None, user)

        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "gender": user.gender,
            "age": user.age,
            "phone_number": user.phone_number,
            "photo_url": user.photo_url,
        }

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "data": user_data,
        }
