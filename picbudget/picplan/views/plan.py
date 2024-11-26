from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from ..serializers import (
    PlanSerializer,
    PlanCreateUpdateSerializer,
    PlanDetailSerializer,
)
from ..models import Plan


# Create your views here.
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    def get_queryset(self):
        # Filter plans based on the logged-in user
        return Plan.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # Use different serializers for different actions
        if self.action in ["create", "update", "partial_update"]:
            return PlanCreateUpdateSerializer
        if self.action == "detail":
            return PlanDetailSerializer
        return PlanSerializer

    def perform_create(self, serializer):
        # Ensure the plan is tied to the logged-in user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        """
        Retrieve all transactions related to a specific plan.
        """
        plan = self.get_object()
        transactions = Transaction.objects.filter(
            wallet__in=plan.wallets.all(),
            labels__in=plan.labels.all(),
            user=request.user,
        ).distinct()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def detail(self, request, pk=None):
        """
        Retrieve a detailed view of the plan, including progress, trends, and spending analysis.
        """
        plan = self.get_object()
        serializer = PlanDetailSerializer(plan)
        return Response(serializer.data)
