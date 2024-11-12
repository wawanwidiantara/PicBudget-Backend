# views.py
from rest_framework.views import APIView
from django.db.models import Sum, Case, When, F
from rest_framework import generics, permissions
from ..models.wallet import Wallet
from picbudget.transactions.models import Transaction
from ..serializers.wallet import WalletSerializer
from rest_framework.response import Response
from django.db import models


class WalletListCreateView(generics.ListCreateAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})


class TotalBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        total_wallet_balance = (
            Wallet.objects.filter(user=user).aggregate(Sum("balance"))["balance__sum"]
            or 0
        )
        total_transaction_amount = (
            Transaction.objects.filter(wallet__user=user).aggregate(
                total=Sum(
                    Case(
                        When(type="income", then=F("amount")),
                        When(type="expense", then=-F("amount")),
                        default=0,
                        output_field=models.DecimalField(),
                    )
                )
            )["total"]
            or 0
        )

        total_balance = total_wallet_balance + total_transaction_amount
        return Response({"data": {"total_balance": total_balance}})
