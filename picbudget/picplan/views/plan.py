from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers.plan import (
    PlanSerializer,
    PlanListSerializer,
    PlanDetailSerializer,
)
from ..models.plan import Plan
from picbudget.transactions.models import Transaction
from picbudget.transactions.serializers.transaction import TransactionSerializer

# Create your views here.
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)

    def get_serializer_class(self):
        if self.action == "list":
            return PlanListSerializer
        elif self.action in ["detail", "retrieve"]:
            return PlanDetailSerializer
        return PlanSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """
        Retrieve all transactions related to a specific plan.
        """
        plan = self.get_object()
        transactions = Transaction.objects.filter(
            wallet__in=plan.wallets.all(),
            labels__in=plan.labels.all(),
        ).distinct()
        serializer = TransactionSerializer(transactions, many=True)
        return Response({"data": serializer.data})
