from django.urls import path
from .views.transaction import (
    TransactionListCreateView,
    TransactionDetailView,
)
from .views.details import (
    TransactionItemListCreateView,
    TransactionItemDetailView,
)

urlpatterns = [
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list"),
    path(
        "transactions/<uuid:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path(
        "transaction-items/",
        TransactionItemListCreateView.as_view(),
        name="transaction-item-list",
    ),
    path(
        "transaction-items/<uuid:pk>/",
        TransactionItemDetailView.as_view(),
        name="transaction-item-detail",
    ),
]
