from rest_framework import generics, permissions
from ..models.transaction import Transaction
from ..models.detail import TransactionDetail
from ..serializers.details import TransactionItemSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response


class TransactionItemListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return TransactionDetail.objects.filter(
            transaction__wallet__user=self.request.user
        )

    def perform_create(self, serializer):
        transaction = Transaction.objects.get(
            id=self.request.data["transaction"], wallet__user=self.request.user
        )
        serializer.save(transaction=transaction)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})


class TransactionItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionDetail.objects.filter(
            transaction__wallet__user=self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})
