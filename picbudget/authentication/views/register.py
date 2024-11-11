from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from ..serializers.register import (
    RegisterSerializer,
    RegisterPersonalDataSerializer,
)
from ..serializers.otp import (
    OTPSerializer,
    VerifyOTPSerializer,
)
import logging

logger = logging.getLogger(__name__)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "User registered successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def resend_otp(self, request):
        serializer = OTPSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            otp_instance = serializer.save()
            return Response(
                {"message": "OTP sent to email."}, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def verify_otp(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "OTP verified successfully."}, status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def register_personal_data(self, request):
        user = request.user
        serializer = RegisterPersonalDataSerializer(user, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            return Response(
                {"message": "Registration completed successfully."},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
