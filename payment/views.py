
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from mapalo.models import Profile
import requests
import os
import datetime


def paymentFailed(request):
    return render(request, 'payments/payment_failed.html')

def paymentSuccess(request):
    return render(request, 'payments/payment_success.html')

def subscriptionPlans(request):
    plans = Plan.objects.all()
    return render(request, 'payments/sub_plans.html', {'plans':plans})

def subscriptions(request):
    user_email = request.user.email
    subs = Subscriptions.objects.filter(payer_email=user_email)
    return render(request, 'payments/subscriptions.html', {"subs": subs})


def PlanDetail(request, plan_id):
    if request.user.is_authenticated:
        user_email = request.user.email
        if Subscriptions.objects.filter(payer_email=user_email).exists():
            plan = MyPlan.objects.get(pk=plan_id)
            return render(request, 'payments/plan_detail.html', {'plan':plan})
        else:
            plan = Plan.objects.get(pk=plan_id)
            return render(request, 'payments/plan_detail.html', {'plan':plan})
    else:
        plan = Plan.objects.get(pk=plan_id)
        request.session['my_plan'] = f'{plan.id}'
        return render(request, 'payments/plan_detail.html', {'plan':plan})
    

""" def mtn_monthly_pay(request):
    pass

def mtn_five_months_pay(request):
    pass


def mtn_yearly_pay(request):
    pass


def airtel_monthly_pay(request):
    pass

def airtel_five_months_pay(request):
    pass

def airtel_yearly_pay(request):
    pass """


"""def get_paypal_access_token():
    client_id = settings.PAYPAL_CLIENT_ID
    secret = settings.PAYPAL_SECRET_KEY

    response = requests.post(
        'https://api-m.sandbox.paypal.com/v1/oauth2/token',
        headers={"Accept": "application/json"},
        data={'grant_type': 'client_credentials'},
        auth=(client_id, secret),
    )

    return response.json()['access_token']

@login_required()
def monthly_subscription(request):
    access_token = get_paypal_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }

    if Subscriptions.objects.filter(user=request.user).exists():
        data = '{ "plan_id": "", "start_time": f"{datetime.datetime.now}", "quantity": "1", "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, "email_address": f"{request.user.email}", "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, "address": { "address_line_1": f"{request.user.profile.address}", "MA", "postal_code": "10101", "country_code": "ZM" } } }, "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans//" } }'

        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)

        if response.status_code == 201 and response.status == "ACTIVE":
            my_status = Profile.objects.filter(user=request.user)
            if my_status.has_paid:
                pass
            else:
                my_status.has_paid=True
                my_status.save()

            Subscriptions.objects.create(
                user=request.user,
                amount=499,
                plan_id=f'P-12794774VS361393VNAGURBQ',
                subscription_id=f'{response.id}',
                status="ACTIVATE",
                plan_type="Monthly Plan",
                expires_on=datetime.datetime.now + datetime.timedelta(days=30),
            )
        else:
            return redirect('payment-failed')
    else:

    data = '{ "plan_id": "P-9C054632KM119774NNB3WXKA","quantity": "1", "custom_id": "S-000555", "shipping_amount": {"currency_code": "USD", "value": "0"}, "start_time": f"{datetime.datetime.now}", "quantity": "1", "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, "email_address": f"{request.user.email}", "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, "address": { "address_line_1": f"{request.user.profile.address}", "MA", "postal_code": "10101", "country_code": "ZM" } } }, "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans//" } }'
    response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)
    if response.status_code == 201 and response.status == "ACTIVE":
        my_status = Profile.objects.filter(user=request.user)
        if my_status.has_paid:
            pass
        else:
            my_status.has_paid=False
            my_status.has_paid=True
            my_status.save()
        Subscriptions.objects.create(
            user=request.user,
            amount=499,
            plan_id=f'P-9C054632KM119774NNB3WXKA',
            subscription_id=f'{response.id}',
            status="ACTIVATE",
            plan_type="Monthly Plan",
            expires_on=datetime.datetime.now + datetime.timedelta(days=30),
        )
        return redirect('payment-success')
    else:
        return redirect('payment-failed')




@login_required()
def annual_subscription(request):
    access_token = get_paypal_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }

    if Subscriptions.objects.filter(user=request.user).exists():
        data = '{ "plan_id": "P-8CN33038UD811140GNAGUVFA", "start_time": f"{datetime.datetime.now}", "quantity": "1", "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, "email_address": f"{request.user.email}", "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, "address": { "address_line_1": f"{request.user.profile.address}", "MA", "postal_code": "10101", "country_code": "ZM" } } }, "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans//" } }'

        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)

        if response.status_code == 201 and response.status == "ACTIVE":
            my_status = Profile.objects.filter(user=request.user)
            if my_status.has_paid:
                pass
            else:
                my_status.has_paid=True
                my_status.save()

            Subscriptions.objects.create(
                user=request.user,
                amount=499,
                plan_id=f'P-8CN33038UD811140GNAGUVFAI',
                subscription_id=f'{response.id}',
                status="ACTIVATE",
                plan_type="Yearly Plan",
                expires_on=datetime.datetime.now + datetime.timedelta(days=30),
            )
        else:
            return redirect('payment-failed')
        
    else:

    data = '{ "plan_id": "P-1G61200532578983DNB3W4GY","quantity": "1", "custom_id": "S-00666", "shipping_amount": {"currency_code": "USD", "value": "0"}, "start_time": f"{datetime.datetime.now}", "quantity": "1", "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, "email_address": f"{request.user.email}", "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, "address": { "address_line_1": f"{request.user.profile.address}", "MA", "postal_code": "10101", "country_code": "ZM" } } }, "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans//" } }'
    response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)
    if response.status_code == 201 and response.status == "ACTIVE":
        my_status = Profile.objects.filter(user=request.user)
        if my_status.has_paid:
            pass
        else:
            my_status.has_paid=False
            my_status.has_paid=True
            my_status.save()
        Subscriptions.objects.create(
            user=request.user,
            amount=5500,
            plan_id=f'P-1G61200532578983DNB3W4GY',
            subscription_id=f'{response.id}',
            status="ACTIVATE",
            plan_type="Yearly Plan",
            expires_on=datetime.datetime.now + datetime.timedelta(days=30),
        )
        return redirect('payment-success')
    else:
        return redirect('payment-failed')
    
@login_required()
def five_months_subscription(request):
    access_token = get_paypal_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }

    if Subscriptions.objects.filter(user=request.user).exists():
        data = '{ "plan_id": "P-6TH570075T6714226NAGUY7Y", "start_time": f"{datetime.datetime.now}", "quantity": "1", "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, "email_address": f"{request.user.email}", "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, "address": { "address_line_1": f"{request.user.profile.address}", "MA", "postal_code": "10101", "country_code": "ZM" } } }, "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans//" } }'

        response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)

        if response.status_code == 201 and response.status == "ACTIVE":
            my_status = Profile.objects.filter(user=request.user)
            if my_status.has_paid:
                pass
            else:
                my_status.has_paid=True
                my_status.save()

            Subscriptions.objects.create(
                user=request.user,
                amount=499,
                plan_id=f'P-6TH570075T6714226NAGUY7YA',
                subscription_id=f'{response.id}',
                status="ACTIVATE",
                plan_type="Five(5) Months Plan",
                expires_on=datetime.datetime.now + datetime.timedelta(days=30),
            )
        else:
            return redirect('payment-failed')
    else:

    data = '{' 
    ' "plan_id": "P-83U34622AY3364234NB3W2AQ",'
    ' "quantity": "1", '
    ' "shipping_amount": {"currency_code": "USD", "value": "0"}, '
    ' "subscriber": { "name": { "given_name": f"{request.user.first_name}", "surname": f"{request.user.last_name}" }, '
    ' "email_address": f"{request.user.email}", '
    ' "shipping_address": { "name": { f"{request.user.first_name}": f"{request.user.last_name}" }, '
    ' "address": { "address_line_1": f"{request.user.profile.address}", '
    ' "MA",' 
    ' "postal_code": "10101", '
    ' "country_code": "ZM" } } }, '
    ' "application_context": { "brand_name": f"{request.user.profile.business}", "locale": "en-US", "shipping_preference": "NO_SHIPPING", "user_action": "SUBSCRIBE_NOW", "payment_method": { "payer_selected": "PAYPAL", "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED" }, "return_url": "https://sophans/payment/payment_success/", "cancel_url": "https://sophans.com/payment/subscription_plans/" } ' \
    '  }'

    response = requests.post('https://api-m.sandbox.paypal.com/v1/billing/subscriptions', headers=headers, data=data)

    if response.status_code == 201 and response.status == "ACTIVE":
        my_status = Profile.objects.filter(user=request.user)
        if my_status.has_paid:
            pass
        else:
            my_status.has_paid=False
            my_status.has_paid=True
            my_status.save()

        Subscriptions.objects.create(
            user=request.user,
            amount=2350,
            plan_id=f'P-83U34622AY3364234NB3W2AQ',
            subscription_id=f'{response.id}',
            status="ACTIVATE",
            plan_type="Five(5) Months Plan",
            expires_on=datetime.datetime.now + datetime.timedelta(days=30),
        )
        return redirect('payment-success')
    else:
        return redirect('payment-failed')





            
def suspend_subscription(request):
    #token = settings.PAYPAL_ACCESS_TOKEN
    token = get_paypal_access_token()
    subs = Subscriptions.objects.latest("created_at").filter(user=request.user)
    sub_id = subs.subscription_id
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = '{ "reason": "Need a Break" }'

    requests.post(f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{sub_id}/suspend', headers=headers, data=data)
    

def cancel_subscription(request):
    #token = settings.PAYPAL_ACCESS_TOKEN
    token = get_paypal_access_token()
    subs = Subscriptions.objects.latest("created_at").filter(user=request.user)
    sub_id = subs.subscription_id
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = '{ "reason": "Not satisfied with the service" }'

    requests.post(f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{sub_id}/cancel', headers=headers, data=data)


def activate_subscription(request):
    #token = settings.PAYPAL_ACCESS_TOKEN
    token = get_paypal_access_token()
    subs = Subscriptions.objects.latest("created_at").filter(user=request.user)
    sub_id = subs.subscription_id
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = '{ "reason": "Reactivating the subscription" }'

    requests.post(f'https://api-m.sandbox.paypal.com/v1/billing/subscriptions/{sub_id}/activate', headers=headers, data=data)







def verify_paypal_webhook(request, payload: dict[str, any]):
    #token = settings.PAYPAL_ACCESS_TOKEN
    token = get_paypal_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    body = {
        "auth_algo": request.headers.get("Paypal-Auth-Algo"),
        "cert_url": request.headers.get("Paypal-Cert-Url"),
        "transmission_id": request.headers.get("Paypal-Transmission-Id"),
        "transmission_sig": request.headers.get("Paypal-Transmission-Sig"),
        "transmission_time": request.headers.get("Paypal-Transmission-Time"),
        "webhook_id": os.getenv("PAYPAL_WEBHOOK_ID"),  # Match it on PayPal dashboard
        "webhook_event": json.loads(request.body.decode('utf-8'))
    }

    response = requests.post("https://api-m.paypal.com/v1/notifications/verify-webhook-signature", json=body, headers=headers)
    return response.json().get("verification_status") == "SUCCESS"




@csrf_exempt
def paypal_webhook_functions(request):
    
    event_body = json.loads(request.body.decode('utf-8'))

    event_type = event_body.get('event_type')
    resource = event_body.get('resource')

    verify_paypal_webhook(request, payload=event_body)

    if event_type == "BILLING.SUBSCRIPTION.CREATED":
        # Store new payer
        
        payer_email = resource.get("subscriber", {}).get("email_address")
        payer_first_name = resource.get("subscriber", {}).get("name", {}).get("given_name")
        payer_last_name = resource.get("subscriber", {}).get("first_name")
        plan_id = resource.get("plan_id")
        plan_name = resource.get("plan", {}).get("name")
        sub_id = resource.get("id")
        
        payer_id = resource.get("subscriber", {}).get("payer_id")

        next_billing_time = resource.get("billing_info", {}).get("next_billing_time")
        amount = resource.get("billing_info", {}).get("last_payment", {}).get("amount", {}).get("value")

        

        Subscriptions.objects.create(
            payers_id=payer_id,
            payer_email=payer_email,
            payers_first_name=payer_first_name,
            payers_last_name=payer_last_name,
            amount=amount,
            plan_id=plan_id,
            subscription_id=sub_id,
            status="ACTIVE",
            plan_type=plan_name,
            expires_at=next_billing_time,
        )

    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        sub_id = resource.get("id")
        Subscriptions.objects.filter(subscription_id=sub_id).update(status="CANCELLED")

    elif event_type == "BILLING.SUBSCRIPTION.SUSPENDED":
        sub_id = resource.get("id")
        Subscriptions.objects.filter(subscription_id=sub_id).update(status="SUSPENDED")

    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        sub_id = resource.get("id")
        Subscriptions.objects.filter(subscription_id=sub_id).update(status="ACTIVE")

    elif event_type == "BILLING.SUBSCRIPTION.EXPIRED":
        sub_id = resource.get("id")
        Subscriptions.objects.filter(subscription_id=sub_id).update(status="EXPIRED")

    return JsonResponse({'status': 'ok'})
    """
