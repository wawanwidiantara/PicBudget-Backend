from rest_framework.routers import SimpleRouter
from .views.account import UserViewSet

router = SimpleRouter(trailing_slash=False)
router.register("account", UserViewSet, basename="account")

urlpatterns = router.urls
