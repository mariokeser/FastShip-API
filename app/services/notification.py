from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr
from fastapi import BackgroundTasks
from app.config import notification_settings
from app.utils import TEMPLATE_DIR
from twilio.rest import Client





class NotificationService:
    def __init__(self, tasks: BackgroundTasks):
        self.tasks = tasks
        self.fastmail = FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(exclude={"TWILIO_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP"}),
                TEMPLATE_FOLDER=TEMPLATE_DIR))

        self.twilio_client = Client(
            username=notification_settings.TWILIO_SID,
            password=notification_settings.TWILIO_AUTH_TOKEN)

    async def send_email(
            self,
            recipients: list[EmailStr],
            subject: str,
            body: str
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=MessageType.plain,

            )
        )

    async def send_email_with_template(
            self,
            recipients: list[EmailStr],
            subject: str,
            context: dict,
            template_name: str
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                template_body=context,
                subtype=MessageType.html
            ),
            template_name=template_name
        )

    async def send_whatsapp(self, to: str, body: str):
       self.tasks.add_task(
        self.twilio_client.messages.create,
            from_=notification_settings.TWILIO_WHATSAPP,
            to=f"whatsapp:{to}",
            body=body
        )

