from django.urls import path
from .views.label import (
    LabelListCreateView,
    LabelDetailView,
)

urlpatterns = [
    path("labels/", LabelListCreateView.as_view(), name="label-list"),
    path("labels/<uuid:pk>/", LabelDetailView.as_view(), name="label-detail"),
]
