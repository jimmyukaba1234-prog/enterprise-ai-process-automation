"""
WhatsApp webhook payload parser.
"""


def parse_whatsapp_message(payload: dict):

    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        messages = value.get("messages", [])

        if not messages:
            return None

        message = messages[0]

        if message.get("type") != "text":
            return None

        phone_number = message.get("from")
        text_body = message.get("text", {}).get("body", "")

        if not phone_number or not text_body:
            return None

        return {
            "phone_number": phone_number,
            "message": text_body
        }

    except Exception:
        return None