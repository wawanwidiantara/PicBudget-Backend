from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views.register import RegisterViewSet

router = SimpleRouter(trailing_slash=False)
router.register("auth", RegisterViewSet, basename="auth")

urlpatterns = router.urls
