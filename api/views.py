import os
import time

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from rest_framework import generics, permissions
from .models import Wallet, Transaction, TransactionItem
from .serializers import (
    WalletSerializer,
    TransactionSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.db import models
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import cv2
import numpy as np
from .processors.page_extractor import PageExtractor
from .processors.text_extractor import TextExtractor
from .processors.receipt_processor import ReceiptProcessor
from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from urllib.parse import urlparse
from django.core.files import File
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import logging
from django.utils.timezone import now

User = get_user_model()

logger = logging.getLogger(__name__)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "dob": user.dob,
            "gender": user.gender,
            "phone_number": user.phone_number,
        }
        return Response(data, status=status.HTTP_200_OK)


class CreateWalletAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        wallet_name = request.data.get("wallet_name")
        balance = request.data.get("balance", 0)

        if not wallet_name:
            return Response(
                {"error": "Wallet name is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        wallet = Wallet.objects.create(
            user=request.user, wallet_name=wallet_name, balance=balance
        )

        serializer = WalletSerializer(wallet, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateWalletBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, wallet_id, *args, **kwargs):
        try:
            # Get the specified wallet for the authenticated user
            wallet = Wallet.objects.get(id=wallet_id, user=request.user)

            # Get the new balance from the request data
            new_balance = request.data.get("balance")
            if new_balance is None:
                return Response(
                    {"error": "No balance provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Update the balance
            wallet.balance = new_balance
            wallet.save()

            # Return the updated wallet data
            serializer = WalletSerializer(wallet, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found or does not belong to the user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WalletListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallets = Wallet.objects.filter(user=request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TotalAmountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_amount = (
            Wallet.objects.filter(user=request.user).aggregate(
                total=models.Sum("balance")
            )["total"]
            or 0
        )
        return Response({"total_amount": total_amount}, status=status.HTTP_200_OK)


class TotalTransactionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_transactions = (
            Transaction.objects.filter(wallet__user=request.user).aggregate(
                total=models.Sum("amount")
            )["total"]
            or 0
        )
        return Response(
            {"total_transactions": total_transactions}, status=status.HTTP_200_OK
        )


class WalletDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        wallet = Wallet.objects.get(id=self.request.data["wallet"])
        wallet.balance -= serializer.validated_data["amount"]
        wallet.save()
        serializer.save()

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user).order_by(
            "-created_at"
        )


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(wallet__user=self.request.user)


class ExtractTextAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Save the uploaded file temporarily
            format_fname = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}.{file.name.split('.')[-1]}"
            file_name = default_storage.save(f"receipts/{format_fname}", file)
            file_url = default_storage.url(file_name)

            # Read the file content for processing
            file.seek(0)  # Ensure the file pointer is at the beginning
            file_content = file.read()
            np_img = np.frombuffer(file_content, np.uint8)

            if np_img.size == 0:
                return Response(
                    {"error": "File buffer is empty"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            original_image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            if original_image is None:
                return Response(
                    {"error": "Failed to decode image"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Make a copy of the original image for processing
            image_for_processing = original_image.copy()

            # Process the image
            print("Processing the image...")  # Debug print
            start_time = time.time()
            page_extractor = PageExtractor(
                image_array=image_for_processing, remove_background="n"
            )
            preprocessed_image = page_extractor.preprocess_image()
            print(f"Processing time: {time.time() - start_time} seconds")  # Debug print

            preprocessed_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_GRAY2BGR)

            start_time = time.time()
            print("Extracting text from the image...")  # Debug print
            text_extractor = TextExtractor(preprocessed_image)
            extracted_text = text_extractor.extracted_text
            print(f"Extraction time: {time.time() - start_time} seconds")  # Debug print

            print("Model implementation...")  # Debug print
            start_time = time.time()
            model_path = "api/picbudget_bilstm/"
            processor = ReceiptProcessor(model_path)
            result = processor.process_receipt(extracted_text)
            result["receipt_image_url"] = request.build_absolute_uri(file_url)
            print("Model implementation done...")  # Debug print
            print(
                f"Model implementation time: {time.time() - start_time} seconds"
            )  # Debug print

            # Return the extracted result for user review
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreateTransactionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            wallet_id = request.data.get("wallet")
            if not wallet_id:
                return Response(
                    {"error": "No wallet provided"}, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                wallet = Wallet.objects.get(id=wallet_id, user=request.user)
            except Wallet.DoesNotExist:
                return Response(
                    {"error": "Wallet not found or does not belong to the user"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extract transaction details from the request
            ocr_data = request.data.get("ocr_data")
            if not ocr_data:
                return Response(
                    {"error": "No OCR data provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            amount = ocr_data.get("total")
            location = ocr_data.get("address")
            date = ocr_data.get("date")
            items = ocr_data.get("items")
            receipt_image_url = ocr_data.get("receipt_image_url")

            if not amount or not date or not items:
                return Response(
                    {"error": "Missing transaction details"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Download the image file from the URL
            parsed_url = urlparse(receipt_image_url)

            # Create a temporary file to save the downloaded image
            image_filename = os.path.basename(parsed_url.path)
            temp_image_path = os.path.join(
                settings.MEDIA_ROOT, "receipts", image_filename
            )

            # Create a transaction with the confirmed data
            with open(temp_image_path, "rb") as f:
                transaction = Transaction(
                    wallet=wallet,
                    amount=amount,
                    location=location,
                    date=datetime.strptime(date, "%d/%m/%Y"),
                    receipt_image=File(f, name=image_filename),
                    ocr_data=ocr_data,
                )
                transaction.save()

            total_transactions = (
                Transaction.objects.filter(wallet__user=request.user).aggregate(
                    total=models.Sum("amount")
                )["total"]
                or 0
            )

            wallet.balance -= total_transactions
            wallet.save()

            # Create TransactionItem entries
            for item in items:
                TransactionItem.objects.create(
                    transaction=transaction,
                    item_name=item["item"],
                    item_price=item["price"],
                )

            # Remove the temporary image file
            os.remove(temp_image_path)

            # Return the transaction data with the full URL for the receipt_image
            serializer = TransactionSerializer(
                transaction, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create a wallet for the user
        balance = serializer.validated_data.get("balance", 0)
        wallet = Wallet.objects.create(user=user, wallet_name="main", balance=balance)

        headers = self.get_success_headers(serializer.data)
        response_data = serializer.data
        response_data["wallet_id"] = wallet.id

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


class ValidateEmailPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"message": "Email and password are valid"}, status=status.HTTP_200_OK
        )


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                print("Refresh token not provided")  # Debug print
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            print(f"Received refresh token: {refresh_token}")  # Debug print

            token = RefreshToken(refresh_token)
            print(f"Token before blacklisting: {token}")  # Debug print
            token.blacklist()
            print("Token blacklisted successfully")  # Debug print

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            print(f"TokenError: {e}")  # Debug print
            return Response(
                {"error": "Invalid token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeyError as e:
            print(f"KeyError: {e}")  # Debug print
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError as e:
            print(f"AttributeError: {e}")  # Debug print
            return Response(
                {"error": "Invalid token", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(f"Exception: {e}")  # Debug print
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
