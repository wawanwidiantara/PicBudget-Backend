from django.urls import path

from .views import (
    UserCreateView,
    TransactionListCreateView,
    TransactionDetailView,
    ExtractTextAPIView,
    CreateTransactionAPIView,
    RegisterView,
    LoginView,
    WalletListView,
    TotalAmountView,
    TotalTransactionsView,
    LogoutView,
    UserDetailView,
    UpdateWalletBalanceView,
    CreateWalletAPIView,
    ValidateEmailPasswordView,
)

urlpatterns = [
    path("user/", UserDetailView.as_view(), name="user_detail"),
    path("users/", UserCreateView.as_view(), name="user-create"),
    path("create-wallet/", CreateWalletAPIView.as_view(), name="create-wallet"),
    path("wallets/", WalletListView.as_view(), name="wallet_list"),
    path(
        "update-wallet-balance/<int:wallet_id>/",
        UpdateWalletBalanceView.as_view(),
        name="update-wallet-balance",
    ),
    path("total-amount/", TotalAmountView.as_view(), name="total_amount"),
    path(
        "total-transactions/",
        TotalTransactionsView.as_view(),
        name="total_transactions",
    ),
    path(
        "transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "transactions/<int:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
    path("extract/", ExtractTextAPIView.as_view(), name="extract-text"),
    path(
        "create-transaction/",
        CreateTransactionAPIView.as_view(),
        name="create-transaction",
    ),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "validate-email-password/",
        ValidateEmailPasswordView.as_view(),
        name="validate-email-password",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
