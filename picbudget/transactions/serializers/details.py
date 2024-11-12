from rest_framework import serializers
from ..models.detail import TransactionDetail


class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetail
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }
