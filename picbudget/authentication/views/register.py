from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from ..serializers.register import (
    RegisterSerializer,
    PersonalDataSerializer,
)


class RegisterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "User registered successfully. OTP sent to email."},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="register/personal-data")
    def personal_data(self, request):
        user = request.user
        serializer = PersonalDataSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"message": "Registration completed successfully."},
            status=status.HTTP_200_OK,
        )
