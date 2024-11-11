from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import SimpleRouter
from .views.register import RegisterViewSet
from .views.login import LoginViewSet
from .views.otp import OTPViewSet

API_PREFIX = "auth"
router = SimpleRouter(trailing_slash=False)
router.register(API_PREFIX, RegisterViewSet, basename="register")
router.register(API_PREFIX, LoginViewSet, basename="login")
router.register(API_PREFIX, OTPViewSet, basename="otp")

urlpatterns = [
    path(
        f"{API_PREFIX}/reset-password",
        auth_views.PasswordResetView.as_view(),
        name="reset_password",
    ),
    path(
        f"{API_PREFIX}/reset-password-sent",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        f"{API_PREFIX}/reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        f"{API_PREFIX}/reset-password-complete",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

urlpatterns += router.urls
