from django.urls import path
from rest_framework.routers import SimpleRouter
from .views.register import RegisterViewSet
from .views.login import LoginViewSet
from .views.otp import OTPViewSet
from .views.reset_password import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

API_PREFIX = "auth"
router = SimpleRouter(trailing_slash=True)
router.register(API_PREFIX, RegisterViewSet, basename="register")
router.register(API_PREFIX, LoginViewSet, basename="login")
router.register(API_PREFIX, OTPViewSet, basename="otp")

urlpatterns = [
    path(
        f"{API_PREFIX}/password-reset/",
        PasswordResetRequestView.as_view(),
        name="password_reset",
    ),
    path(
        f"{API_PREFIX}/password-reset-confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

urlpatterns += router.urls
