from asgiref.sync import async_to_sync
from celery import Celery
from ..config import db_settings, notification_settings
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from app.utils import TEMPLATE_DIR
from pydantic import EmailStr
from twilio.rest import Client




app = Celery(
    "api_tasks",
    broker=db_settings.REDIS_URL(db=9),
    backend=db_settings.REDIS_URL(db=9),
    broker_connection_retry_on_startup=True
)




twilio_client = Client(
        username=notification_settings.TWILIO_SID,
        password=notification_settings.TWILIO_AUTH_TOKEN)


fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(exclude={"TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP"}),
                TEMPLATE_FOLDER=TEMPLATE_DIR))

send_message = async_to_sync(fastmail.send_message)




@app.task
def send_email_with_template(
        recipients: list[EmailStr],
        subject: str,
        context: dict,
        template_name: str
):
        send_message(
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                template_body=context,
                subtype=MessageType.html
            ),
            template_name=template_name
        )



@app.task
def send_whatsapp(to: str, body: str):
    twilio_client.messages.create(
        from_=notification_settings.TWILIO_WHATSAPP,
        to=f"whatsapp:{to}",
        body=body
    )


# Append new lines in the log file
@app.task
def add_log(log: str) -> None:
    with open("file.log", "a") as file:
        file.write(f"{log}\n")