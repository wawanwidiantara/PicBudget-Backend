from django.urls import path
from .views.receipt import ReceiptView

urlpatterns = [path("picscan-receipt/", ReceiptView.as_view(), name="receipt-upload")]
