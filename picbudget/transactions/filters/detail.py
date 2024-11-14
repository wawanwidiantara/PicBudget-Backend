import django_filters
from ..models.detail import TransactionDetail


class TransactionItemFilter(django_filters.FilterSet):
    transaction = django_filters.UUIDFilter(
        field_name="transaction__id", required=False
    )

    class Meta:
        model = TransactionDetail
        fields = ["transaction"]
