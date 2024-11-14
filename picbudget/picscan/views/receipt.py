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
from picbudget.transactions.serializers.details import TransactionItemSerializer


from django.apps import apps
from PIL import Image
import numpy as np
import cv2
from ..utils.processors import (
    image_processing,
    extract_text,
)

import os
from paddleocr import PaddleOCR

import logging

logger = logging.getLogger(__name__)


class ReceiptView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            receipt = serializer.validated_data["receipt"]
            image_data = receipt.read()
            path = default_storage.save(
                "receipts/picscan/" + receipt.name, ContentFile(image_data)
            )

            # Image processing
            logger.info("Image processing running")
            image = cv2.cvtColor(
                np.array(Image.open(ContentFile(image_data))), cv2.COLOR_RGB2BGR
            )
            image_processor = image_processing.ImageProcessor(image)
            image = image_processor.preprocess_image()

            # OCR
            logger.info("OCR running")
            extract_text_processor = extract_text.TextExtractor(image)
            extracted_text = extract_text_processor.extracted_text

            # Model processing
            logger.info("Model processing running")
            processor = apps.get_app_config("picscan").receipt_processor
            result = processor.process_receipt(extracted_text)
            url = request.build_absolute_uri(default_storage.url(path))

            logger.info("Saving transaction")
            # check if request data has user id and wallet id and save the transaction
            if "user_id" in request.data and "wallet_id" in request.data:
                user = User.objects.get(id=request.data["user_id"])
                wallet = Wallet.objects.get(id=request.data["wallet_id"], user=user)
                transaction = Transaction.objects.create(
                    wallet=wallet,
                    amount=result["total"],
                    transaction_date=result["date"],
                    # if location is not available, set it to None
                    location=result.get("location", None),
                    receipt=path,
                    method="picscan",
                    status="unconfirmed",
                )
                transaction.save()

                logger.info("Saving transaction details")
                # result["items"] is a list of dictionaries, each dictionary contains the item details, save them to the database
                for item in result["items"]:
                    detail = TransactionDetail.objects.create(
                        transaction=transaction,
                        item_name=item["item_name"],
                        item_price=item["item_price"],
                    )
                    detail.save()

                transaction_serializer = TransactionSerializer(transaction)
                details_serializer = TransactionItemSerializer(
                    TransactionDetail.objects.filter(transaction=transaction), many=True
                )

                return Response(
                    {
                        "data": {
                            "transaction": transaction_serializer.data,
                            "items": details_serializer.data,
                        }
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "path": url,
                        "result": result,
                    },
                    status=status.HTTP_201_CREATED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# created a new view to change the status of the transaction to confirmed
class ConfirmTransactionView(APIView):
    permission_classes = [IsAuthenticated]

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
