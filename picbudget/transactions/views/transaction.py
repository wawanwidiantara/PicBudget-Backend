from rest_framework import generics, permissions
from ..models.transaction import Transaction
from picbudget.wallets.models import Wallet
from ..serializers.transaction import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.transaction import TransactionFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum

from django.utils import timezone
from datetime import timedelta


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    def perform_create(self, serializer):
        wallet = Wallet.objects.get(
            id=self.request.data["wallet"], user=self.request.user
        )
        serializer.save(wallet=wallet)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})


class TransactionSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        now = timezone.now()

        transactions = Transaction.objects.filter(wallet__user=user)

        total_today = (
            transactions.filter(transaction_date__date=now.date()).aggregate(
                total=Sum("amount")
            )["total"]
            or 0
        )

        total_week = (
            transactions.filter(
                transaction_date__gte=now - timedelta(days=7)
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        total_month = (
            transactions.filter(
                transaction_date__gte=now - timedelta(days=30)
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        total_all = transactions.aggregate(total=Sum("amount"))["total"] or 0

        response_data = {
            "total_today": total_today,
            "total_week": total_week,
            "total_month": total_month,
            "total_all": total_all,
        }

        return Response({"data": response_data})


class TransactionByLabelSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        transactions = Transaction.objects.filter(wallet__user=user)

        totals_by_label = (
            transactions.values("labels__name")
            .annotate(total_amount=Sum("amount"))
            .order_by("labels__name")
        )

        response_data = [
            {
                "label": entry["labels__name"] or "Unlabeled",
                "total_amount": entry["total_amount"] or 0,
            }
            for entry in totals_by_label
        ]

        return Response({"data": response_data})
