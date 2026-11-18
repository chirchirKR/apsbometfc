import base64
from datetime import datetime
import requests
from django.conf import settings


def _base_url():
    return ("https://sandbox.safaricom.co.ke"
            if getattr(settings, "MPESA_ENV", "sandbox").lower() == "sandbox"
            else "https://api.safaricom.co.ke")


def access_token():
    key = getattr(settings, "MPESA_CONSUMER_KEY", "")
    secret = getattr(settings, "MPESA_CONSUMER_SECRET", "")
    if not key or not secret:
        raise ValueError("M-Pesa consumer key/secret are not configured.")
    response = requests.get(
        f"{_base_url()}/oauth/v1/generate",
        params={"grant_type": "client_credentials"},
        auth=(key, secret),
        timeout=25,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def stk_push(phone, amount, account_reference, description):
    shortcode = str(settings.MPESA_SHORTCODE)
    passkey = settings.MPESA_PASSKEY
    callback_url = settings.MPESA_CALLBACK_URL
    if not passkey or not callback_url or "https://" not in callback_url:
        raise ValueError("Configure MPESA_PASSKEY and a public HTTPS MPESA_CALLBACK_URL.")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    token = access_token()
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": getattr(settings, "MPESA_TRANSACTION_TYPE", "CustomerPayBillOnline"),
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference[:12],
        "TransactionDesc": description[:13],
    }
    response = requests.post(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()



def stk_query(checkout_request_id):
    """Ask Daraja for the current status of a previously initiated STK request."""
    shortcode = str(settings.MPESA_SHORTCODE)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{shortcode}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()
    token = access_token()
    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }
    response = requests.post(
        f"{_base_url()}/mpesa/stkpushquery/v1/query",
        json=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
