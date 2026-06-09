
"""
WhatsApp Cloud API message sender.

This module sends chatbot responses back to customers
through Meta WhatsApp Cloud API.
"""

import os
import requests


WHATSAPP_API_VERSION = "v20.0"


def get_whatsapp_config() -> dict:
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN is missing.")

    if not phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID is missing.")

    return {
        "access_token": access_token,
        "phone_number_id": phone_number_id
    }


def send_whatsapp_message(to_phone_number: str, message: str) -> dict:
    config = get_whatsapp_config()

    url = (
        f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
        f"{config['phone_number_id']}/messages"
    )

    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    return response.json()