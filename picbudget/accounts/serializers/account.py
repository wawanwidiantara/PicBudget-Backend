from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "gender",
            "age",
            "phone_number",
            "photo_url",
            "old_password",
            "new_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        old_password = validated_data.pop("old_password", None)
        new_password = validated_data.pop("new_password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if new_password:
            instance.set_password(new_password)

        instance.save()
        return instance

    def validate(self, data):
        user = self.instance
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if old_password and new_password:
            if not user.check_password(old_password):
                raise serializers.ValidationError({"old_password": "Wrong password."})
            if old_password == new_password:
                raise serializers.ValidationError(
                    {
                        "new_password": "New password must be different from the old password."
                    }
                )
        return data
