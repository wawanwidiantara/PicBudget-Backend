from rest_framework import serializers
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
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
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "google_id": {"read_only": True},
            "apple_id": {"read_only": True},
            "email": {"read_only": True},
        }

    def update(self, instance, validated_data):
        photo_url = validated_data.pop("photo_url", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if photo_url:
            if instance.photo_url and os.path.isfile(instance.photo_url.path):
                os.remove(instance.photo_url.path)

            ext = os.path.splitext(photo_url.name)[1]
            new_filename = f"{instance.id}{ext}"
            instance.photo_url.save(new_filename, photo_url, save=False)

        instance.save()
        return instance
