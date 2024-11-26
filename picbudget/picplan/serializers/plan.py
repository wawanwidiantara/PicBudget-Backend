from rest_framework import serializers
from django.db import models
from picbudget.labels.serializers import LabelSerializer
from picbudget.wallets.serializers import WalletSerializer
from picbudget.picplan.models import Plan
from picbudget.transactions.models import Transaction


class PlanSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    wallets = WalletSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()
    is_overspent = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "amount",
            "period",
            "labels",
            "wallets",
            "notify_overspent",
            "progress",
            "is_overspent",
            "created_at",
            "updated_at",
        ]

    def get_progress(self, obj):
        return obj.calculate_progress()

    def get_is_overspent(self, obj):
        return obj.is_overspent()


class PlanCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["name", "amount", "period", "labels", "wallets", "notify_overspent"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class PlanDetailSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    remaining = serializers.SerializerMethodField()
    daily_average = serializers.SerializerMethodField()
    daily_recommended = serializers.SerializerMethodField()
    last_periods = serializers.SerializerMethodField()
    spending_by_labels = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "amount",
            "progress",
            "remaining",
            "daily_average",
            "daily_recommended",
            "last_periods",
            "spending_by_labels",
        ]

    def get_progress(self, obj):
        """Calculate percentage progress."""
        return obj.calculate_progress()

    def get_remaining(self, obj):
        """Calculate remaining budget."""
        total_spent = obj.calculate_progress() * obj.amount / 100
        return obj.amount - total_spent

    def get_daily_average(self, obj):
        """Calculate daily average spending."""
        transactions = Transaction.objects.filter(
            wallet__in=obj.wallets.all(),
            labels__in=obj.labels.all(),
            user=obj.user,
            transaction_date__month=obj.created_at.month,
        )
        total_spent = transactions.aggregate(total=models.Sum("amount"))["total"] or 0
        return total_spent / obj.created_at.day

    def get_daily_recommended(self, obj):
        """Calculate recommended daily spending."""
        now = obj.created_at.day
        days_in_month = 30  # Adjust for actual days in the month
        return obj.amount / days_in_month

    def get_last_periods(self, obj):
        """Generate data for the bar chart of last periods."""
        periods = []
        for month_offset in range(1, 5):  # Adjust the range as needed
            previous_month = obj.created_at.month - month_offset
            transactions = Transaction.objects.filter(
                wallet__in=obj.wallets.all(),
                labels__in=obj.labels.all(),
                user=obj.user,
                transaction_date__month=previous_month,
            )
            total_spent = (
                transactions.aggregate(total=models.Sum("amount"))["total"] or 0
            )
            periods.append(
                {
                    "month": previous_month,
                    "spent": total_spent,
                    "status": "in_limit" if total_spent <= obj.amount else "over_limit",
                }
            )
        return periods

    def get_spending_by_labels(self, obj):
        """Generate data for the pie chart."""
        labels = obj.labels.all()
        data = []
        for label in labels:
            transactions = Transaction.objects.filter(
                labels=label,
                wallet__in=obj.wallets.all(),
                user=obj.user,
                transaction_date__month=obj.created_at.month,
            )
            total_spent = (
                transactions.aggregate(total=models.Sum("amount"))["total"] or 0
            )
            data.append({"label": label.name, "spent": total_spent})
        return data
