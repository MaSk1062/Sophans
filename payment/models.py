from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class ProductID(models.Model):
    prod_id = models.CharField(max_length=255)

    def __str__(self):
        return self.prod_id


class Subscriptions(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payers_id = models.CharField(max_length=255, null=True, default='')
    payer_email = models.EmailField(null=True, default='')
    payers_first_name = models.CharField(max_length=200, null=True, default='')
    payers_last_name = models.CharField(max_length=200, null=True, default='')
    amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, default='')# Amount in USD
    plan_id = models.CharField(max_length=255)  # The associated plan ID
    subscription_id = models.CharField(max_length=255)  # PayPal subscription ID
    status = models.CharField(max_length=50)  # e.g., ACTIVE, PAUSED, CANCELLED
    plan_type = models.CharField(max_length=200, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"



class Plan(models.Model):
    plan_id = models.CharField(max_length=250, default='')
    name = models.CharField(max_length=50, default='')
    price = models.CharField(max_length=12, default='')
    feature_1 = models.CharField(max_length=250, default='')
    feature_2 = models.CharField(max_length=250, default='')
    feature_3 = models.CharField(max_length=250, default='')
    feature_4 = models.CharField(max_length=250, default='')
    feature_5 = models.CharField(max_length=250, default='')
    more = models.CharField(max_length=250, default='')

    def __str__(self):
        return self.name
    

class MyPlan(models.Model):
    plan_id = models.CharField(max_length=250, default='')
    name = models.CharField(max_length=50, default='')
    price = models.CharField(max_length=12, default='')
    feature_1 = models.CharField(max_length=250, default='')
    feature_2 = models.CharField(max_length=250, default='')
    feature_3 = models.CharField(max_length=250, default='')
    feature_4 = models.CharField(max_length=250, default='')
    feature_5 = models.CharField(max_length=250, default='')
    more = models.CharField(max_length=250, default='')

    def __str__(self):
        return f'My Plan{self.name}'