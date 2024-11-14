from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.receipt import ReceiptSerializer
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.permissions import AllowAny, IsAuthenticated

from picbudget.transactions.models.transaction import Transaction
from picbudget.transactions.models.detail import TransactionDetail
from picbudget.wallets.models.wallet import Wallet
from picbudget.accounts.models.accounts import User

from picbudget.transactions.serializers.transaction import TransactionSerializer

import os
from uuid import uuid4

from django.apps import apps
from PIL import Image
import numpy as np
import cv2
from ..utils.processors import (
    image_processing,
    extract_text,
)

import logging

logger = logging.getLogger(__name__)


class ReceiptView(APIView):
    permission_classes = [AllowAny]

    def _process_image(self, image_data):
        image = cv2.cvtColor(
            np.array(Image.open(ContentFile(image_data))), cv2.COLOR_RGB2BGR
        )
        return image_processing.ImageProcessor(image).preprocess_image()

    def _save_transaction_details(self, transaction, items):
        TransactionDetail.objects.bulk_create(
            [
                TransactionDetail(
                    transaction=transaction,
                    item_name=item["item_name"],
                    item_price=item["item_price"],
                )
                for item in items
            ]
        )

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        receipt = serializer.validated_data["receipt"]
        image_data = receipt.read()

        # Save file with UUID
        file_ext = os.path.splitext(receipt.name)[1]
        path = default_storage.save(
            f"receipts/picscan/{uuid4()}{file_ext}", ContentFile(image_data)
        )
        url = request.build_absolute_uri(default_storage.url(path))

        # Process image and extract text
        processed_image = self._process_image(image_data)
        extracted_text = extract_text.TextExtractor(processed_image).extracted_text

        # Process receipt
        processor = apps.get_app_config("picscan").receipt_processor
        result = processor.process_receipt(extracted_text)

        if "user_id" not in request.data or "wallet_id" not in request.data:
            return Response(
                {"path": url, "result": result}, status=status.HTTP_201_CREATED
            )

        # Create transaction
        try:
            user = User.objects.get(id=request.data["user_id"])
            wallet = Wallet.objects.get(id=request.data["wallet_id"], user=user)

            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=result["total"],
                transaction_date=result["date"],
                location=result.get("location"),
                receipt=path,
                method="picscan",
                status="unconfirmed",
            )

            self._save_transaction_details(transaction, result["items"])

            data = TransactionSerializer(transaction).data
            data["receipt"] = url

            return Response({"data": data}, status=status.HTTP_201_CREATED)

        except (User.DoesNotExist, Wallet.DoesNotExist):
            return Response(
                {"error": "Invalid user_id or wallet_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ConfirmTransactionView(APIView):

    def post(self, request, pk):
        try:
            transaction = Transaction.objects.get(pk=pk, wallet__user=request.user)
            transaction.status = "confirmed"
            transaction.save()
            return Response(
                {"message": "Transaction confirmed successfully"},
                status=status.HTTP_200_OK,
            )
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )
