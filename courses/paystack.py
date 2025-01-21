import requests # type: ignore
from django.conf import settings


class Paystack:
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
    BASE_URL = "https://api.paystack.co"

    @staticmethod
    def initialize_transaction(email, amount, metadata=[]):
        url = f"{Paystack.BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {Paystack.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        if metadata:
            data = {
            "email": email,
            "amount": int(amount) * 100,  # Convert to kobo
            "metadata": metadata
            }
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    @staticmethod
    def verify_transaction(reference):
        url = f"{Paystack.BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {Paystack.PAYSTACK_SECRET_KEY}",
        }
        response = requests.get(url, headers=headers)
        return response.json()
