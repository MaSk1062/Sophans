import django_filters
from .models import *


class TenantFilter(django_filters.FilterSet):
    class Meta:
        model = Tenant
        fields = ['name', 'sex', 'bedroom', 'paid', 'added', 'due']



class BedroomFilter(django_filters.FilterSet):
    class Meta:
        model = BedRoom
        fields = ['name', 'total_spaces', 'available_spaces', 'sex']



class BedspaceFilter(django_filters.FilterSet):

    class Meta:
        model = BedSpace
        fields = ['name', 'sex', 'bedroom']

class TransactionFilter(django_filters.FilterSet):
    class Meta:
        model = Transactions
        fields = ['tenant', 'amount', 'paid', 'date']

class ReceiptFilter(django_filters.FilterSet):
    class Meta:
        models = BoardingReceipt
        fields = ['tenant', 'date_created']