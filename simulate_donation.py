import os

import requests
import json
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

data = {
    "verification_token": "73db966b-d603-4ae9-b947-9d8fcb1efdba",
    "message_id": "fed129db-75d6-4e2d-8a41-4765b77aeb22",
    "timestamp": "2024-08-18T19:07:46Z",
    "type": "Subscription",
    "is_public": True,
    "from_name": "laptaka",
    "message": "Hello!",
    "amount": "20.00",
    "url": "https://ko-fi.com/Home/CoffeeShop?txid=00000000-1111-2222-3333-444444444444",
    "email": "example@example.com",
    "currency": "USD",
    "is_subscription_payment": False,
    "is_first_subscription_payment": False,
    "kofi_transaction_id": "00000000-1111-2222-3333-444444444444",
    "shop_items": None,
    "tier_name": None,
    "shipping": None,
}

json_str = json.dumps(data)
encoded_str = urllib.parse.quote(json_str)
final_output = f"data={encoded_str}"

print(final_output)

webhook_url = os.getenv("WEBHOOK_URL")
# webhook_url = "http://localhost:3001/kofi-webhook"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
response = requests.post(webhook_url, data=final_output, headers=headers)

if response.status_code == 200:
    print("POST request sent successfully")
else:
    print(f"Failed to send POST request. Status code: {response.status_code}")
    print(f"Response content: {response.text}")
