"""
FastAPI WhatsApp webhook server.

Receives WhatsApp messages, sends them through the shared chatbot engine,
creates tickets, updates dashboards, and replies back through WhatsApp.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse

from app.channels.whatsapp_parser import parse_whatsapp_message
from app.channels.whatsapp_sender import send_whatsapp_message
from app.chatbot.chatbot_agent import process_customer_message




app = FastAPI(
    title="Waya AI WhatsApp Chatbot API",
    version="1.0.0"
)


@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "WhatsApp AI Chatbot API"
    }


@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params

    mode = params.get("hub.mode")
    verify_token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    expected_token = os.getenv("WHATSAPP_VERIFY_TOKEN")

    print("META TOKEN:", verify_token)
    print("EXPECTED TOKEN:", expected_token)
    
    if mode == "subscribe" and verify_token == expected_token:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(
        content="Verification failed",
        status_code=403
    )


@app.post("/webhook")
async def receive_whatsapp_message(request: Request):
    payload = await request.json()

    parsed_message = parse_whatsapp_message(payload)

    if not parsed_message:
        return JSONResponse(
            content={"status": "ignored"},
            status_code=200
        )

    customer_phone = parsed_message["phone_number"]
    customer_message = parsed_message["message"]

    customer_id = f"WA-{customer_phone}"

    result = process_customer_message(
        customer_id=customer_id,
        message=customer_message
    )

    bot_response = result["bot_response"]

    send_whatsapp_message(
        to_phone_number=customer_phone,
        message=bot_response
    )

    return JSONResponse(
        content={
            "status": "processed",
            "customer_id": customer_id,
            "ticket_id": result["ticket"]["ticket_id"]
        },
        status_code=200
    )