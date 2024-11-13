from rest_framework import serializers


class ReceiptSerializer(serializers.Serializer):
    receipt = serializers.ImageField()

    def validate_receipt_image(self, value):
        if value is None:
            raise serializers.ValidationError("Image is required")
        if not value.name.endswith((".jpg", ".jpeg", ".png")):
            raise serializers.ValidationError("Invalid image format")
        return value
