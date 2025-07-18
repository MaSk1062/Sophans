# utils.py
import requests
import os

def verify_paypal_webhook(request):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_paypal_access_token()}"
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
