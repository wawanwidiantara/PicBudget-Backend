from django.urls import path
from .views.transaction import (
    TransactionListCreateView,
    TransactionDetailView,
)

urlpatterns = [
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list"),
    path(
        "transactions/<uuid:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
