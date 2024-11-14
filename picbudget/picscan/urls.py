from django.urls import path
from .views.receipt import ReceiptView, ConfirmTransactionView

urlpatterns = [
    path("picscan-receipt/", ReceiptView.as_view(), name="receipt-upload"),
    path(
        "picscan-confirm/<uuid:pk>/",
        ConfirmTransactionView.as_view(),
        name="confirm-transaction",
    ),
]
