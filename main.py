import os

import uvicorn
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from constants import wa_token, verify_wa_token, bard_token
from bardapi import Bard
import requests

bard = Bard(token=bard_token)
app = FastAPI()


class WebhookEvent(BaseModel):
    object: str
    entry: list


@app.get("/webhook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and wa_token:
        if mode == "subscribe" and verify_token == verify_wa_token:
            return Response(challenge, status_code=200)

    return Response(status_code=403)


@app.post("/webhook")
async def receive_webhook(event: WebhookEvent):
    if event.object and event.entry:
        changes = event.entry[0].get("changes")
        if (changes and changes[0].get("value")
                and changes[0]["value"].get("messages")
                and changes[0]["value"]["messages"][0]):
            phon_no_id = changes[0]["value"]["metadata"]["phone_number_id"]
            from_number = changes[0]["value"]["messages"][0]["from"]
            try:
                msg_body = changes[0]["value"]["messages"][0]["text"]["body"]
            except:
                msg_body = 'None'
            if msg_body == 'None':
                x = 'Sorry i cant Process the request at a time'
            else:
                x = bard.get_answer(msg_body)['content']
            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "status": "read",
                "text": {"body": f"{x}"},
            }
            header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {wa_token}"
            }
            url = f"https://graph.facebook.com/v16.0/{phon_no_id}/messages"
            response = requests.post(url, json=payload, headers=header)
            if response.ok:
                return Response(status_code=200)
    return Response(status_code=404)


@app.get("/")
async def home():
    return "hello this is webhook setup"

if __name__ == "__main__":
    uvicorn.run(app, port=int(os.environ.get("PORT", 8000)), host="0.0.0.0")
