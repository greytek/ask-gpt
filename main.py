from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from constants import token, verify_token, bard_token
from bardapi import Bard
import requests


bard = Bard(token=bard_token)
app = FastAPI()


class WebhookEvent(BaseModel):
    object: str
    entry: list


@app.get("/webhook")
async def verify_webhook(request: Request, challenge: str = None, token: str = None):
    mode = request.query_params.get("hub.mode")
    verify_wa_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and verify_wa_token == verify_token:
            return challenge

    return Response(status_code=403)


@app.post("/webhook")
async def receive_webhook(event: WebhookEvent):
    if event.object and event.entry:
        changes = event.entry[0].get("changes")
        if (
                changes
                and changes[0].get("value")
                and changes[0]["value"].get("messages")
                and changes[0]["value"]["messages"][0]
        ):
            phon_no_id = changes[0]["value"]["metadata"]["phone_number_id"]
            from_number = changes[0]["value"]["messages"][0]["from"]
            msg_body = changes[0]["value"]["messages"][0]["text"]["body"]

            print("phone number id:", phon_no_id)
            print("from:", from_number)
            print("message body:", msg_body)

            x = bard.get_answer(msg_body)['content']
            print(x)

            payload = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "text": {"body": f"{x}"},
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }
            url = f"https://graph.facebook.com/v17.0/{phon_no_id}/messages?access_token={token}"
            response = requests.post(url, data=payload, headers=headers)
            if response.ok:
                return Response(status_code=200)

    return Response(status_code=404)


async def get_res(msg_body):
    x = bard.get_answer(msg_body)['content']
    print(x)
    return x


@app.get("/")
async def home():
    return "hello this is webhook setup"
