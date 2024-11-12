# filters.py
import django_filters
from ..models.transaction import Transaction


class TransactionFilter(django_filters.FilterSet):
    transaction_date_from = django_filters.DateTimeFilter(
        field_name="transaction_date", lookup_expr="gte", required=False
    )
    transaction_date_to = django_filters.DateTimeFilter(
        field_name="transaction_date", lookup_expr="lte", required=False
    )
    wallet = django_filters.UUIDFilter(field_name="wallet__id", required=False)
    type = django_filters.CharFilter(field_name="type", required=False)

    class Meta:
        model = Transaction
        fields = ["wallet", "type", "transaction_date_from", "transaction_date_to"]
