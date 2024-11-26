from django.urls import path
from .views.plan import PlanViewSet

urlpatterns = [
    path(
        "plans/",
        PlanViewSet.as_view({"get": "list", "post": "create"}),
        name="plan-list",
    ),
    path(
        "plans/<uuid:pk>/",
        PlanViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="plan-detail",
    ),
    path(
        "plans/<uuid:pk>/transactions/",
        PlanViewSet.as_view({"get": "transactions"}),
        name="plan-transactions",
    ),
    path(
        "plans/<uuid:pk>/detail/",
        PlanViewSet.as_view({"get": "detail"}),
        name="plan-detail-view",
    ),
]
