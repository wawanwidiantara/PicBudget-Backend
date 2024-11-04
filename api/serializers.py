from rest_framework import serializers
from .models import User, Wallet, Transaction, TransactionItem
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name", "dob", "gender", "phone_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom user data to the response
        user = self.user
        user_data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "dob": user.dob,
            "gender": user.gender,
            "phone_number": user.phone_number,
        }

        # Wrap user data inside a "data" key
        data["data"] = user_data

        return data


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["id", "wallet_name", "balance"]


class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionItem
        fields = ["id", "transaction", "item_name", "item_price"]


class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionItem
        fields = ["id", "transaction", "item_name", "item_price"]


class TransactionSerializer(serializers.ModelSerializer):
    items = TransactionItemSerializer(many=True)
    receipt_image = serializers.SerializerMethodField()
    formatted_date = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "wallet",
            "receipt_image",
            "amount",
            "location",
            "formatted_date",
            "items",
        ]

    def get_receipt_image(self, obj):
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.receipt_image.url)
        return obj.receipt_image.url

    def get_formatted_date(self, obj):
        return obj.date.strftime("%d/%m/%Y")

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        transaction = Transaction.objects.create(**validated_data)
        for item_data in items_data:
            TransactionItem.objects.create(transaction=transaction, **item_data)
        return transaction


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "name",
            "dob",
            "gender",
            "phone_number",
            "balance",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        balance = validated_data.pop("balance", 0)
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        Wallet.objects.create(user=user, wallet_name="main", balance=balance)
        return user
