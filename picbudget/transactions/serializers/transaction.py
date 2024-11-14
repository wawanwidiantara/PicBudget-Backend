from rest_framework import serializers
from ..models.transaction import Transaction
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from uuid import uuid4


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def create(self, validated_data):
        labels = validated_data.pop("labels", [])
        receipt = validated_data.pop("receipt", None)
        image_data = receipt.read() if receipt else None

        # Generate UUID filename
        if image_data:
            file_ext = os.path.splitext(receipt.name)[1]
            new_filename = f"{uuid4()}{file_ext}"
            path = default_storage.save(
                f"receipts/manual/{new_filename}", ContentFile(image_data)
            )
            validated_data["receipt"] = path

        transaction = Transaction.objects.create(**validated_data)

        if labels:
            transaction.labels.set(labels)

        return transaction
