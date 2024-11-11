from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import SimpleRouter
from .views.register import RegisterViewSet

router = SimpleRouter(trailing_slash=False)
router.register("register", RegisterViewSet, basename="register")

urlpatterns = [
    path(
        "reset_password", auth_views.PasswordResetView.as_view(), name="reset_password"
    ),
    path(
        "reset_password_done",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset_password_complete",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

urlpatterns += router.urls
