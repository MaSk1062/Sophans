from django.db import models
from django.db.models import Count, Sum

class TenantQuerySet(models.QuerySet):
    def get_males(self):
        return self.filter(sex='M').count()
    
    def get_females(self):
        return self.filter(sex='F').count()


class RoomsQuerySet(models.QuerySet):
    def for_males(self):
        return self.filter(sex='M').count()

    def for_females(self):
        return self.filter(sex='F').count()

    def available_rooms(self):
        return self.filter(available_spaces__gte=1).count()


class BedspaceQuerySet(models.QuerySet):
    def for_males(self):
        return self.filter(sex='M').count()

    def for_females(self):
        return self.filter(sex='F').count()


class TransactionQuerySet(models.QuerySet):
    def paid(self):
        return self.filter(paid=True)

    def unpaid(self):
        return self.filter(paid=False)

    def paid_total(self):
        return self.paid().aggregate(
            total=models.Sum('amount')
            )['total'] or 0

    def unpaid_total(self):
        return self.unpaid().aggregate(
            total=models.Sum('amount')
            )['total'] or 0




