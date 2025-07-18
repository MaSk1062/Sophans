from django.urls import path
from payment import views

urlpatterns = [
    path('subscriptions/', views.subscriptions, name="subscriptions"),
    path('subscription_plans/', views.subscriptionPlans, name="subscription-plans"),
    #path('payment_failed/', views.paymentFailed, name="payment-failed"),
    #path('payment_success/', views.paymentSuccess, name="payment-success"),
    #path('monthly_subscription/', views.monthly_subscription, name='monthly-subscription'),
    #path('five_months_subscription/', views.five_months_subscription, name='five-months-subscription'),
    #path('yearly_subscription/', views.annual_subscription, name='yearly-subscription'),
    #path('success/', views.subscription_success, name='success'),
    #path('cancel_subscription/', views.cancel_subscription, name='cancel-subscription'),
    #path('suspend_subscription/', views.suspend_subscription, name='suspend-subscription'),
    #path('activate/', views.activate_subscription, name='reactivate-subscription'),
    #path('mtn_monthly_pay/', views.mtn_monthly_pay, name="mtn-monthly"),
    #path('mtn_five_months_pay/', views.mtn_five_months_pay, name="mtn-five-months"),
    #path('mtn_yearly_pay/', views.mtn_yearly_pay, name="mtn-yearly"),
    #path('airtel_monthly_pay/', views.airtel_monthly_pay, name="airtel-monthly"),
    #path('airtel_five_months_pay/', views.airtel_five_months_pay, name="airtel-five-months"),
    #path('airtel_yearly_pay/', views.airtel_yearly_pay, name="airtel-yearly"),
    path('plan_detail/<int:plan_id>/', views.PlanDetail, name="plan-details"),
    #path('webhooks/', views.paypal_webhook_functions, name='webhooks'),
    
    ]