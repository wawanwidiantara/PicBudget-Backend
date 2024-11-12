from django.urls import path
from rest_framework.routers import SimpleRouter
from .views.wallet import (
    WalletListCreateView,
    WalletDetailView,
    TotalBalanceView,
)

urlpatterns = [
    path("wallets", WalletListCreateView.as_view(), name="wallet-list-create"),
    path("wallets/<uuid:pk>", WalletDetailView.as_view(), name="wallet-detail"),
    path("wallets/total-balance", TotalBalanceView.as_view(), name="total-balance"),
]
