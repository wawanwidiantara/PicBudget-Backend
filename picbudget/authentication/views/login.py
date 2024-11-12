from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from ..serializers.login import LoginSerializer
from rest_framework.permissions import AllowAny


class LoginViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save()
        return Response(response_data, status=status.HTTP_200_OK)
