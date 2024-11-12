from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework import generics, permissions
from ..models.transaction import Transaction
from picbudget.wallets.models import Wallet
from ..serializers.transaction import TransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from ..filters.transaction import TransactionFilter
from rest_framework.response import Response


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})
