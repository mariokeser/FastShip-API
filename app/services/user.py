from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .base import BaseService
from ..core.exceptions import InvalidToken, BadCredentials, ClientNotVerified
from ..database.models import User
from ..utils import generate_access_token, generate_url_safe_token, decode_url_safe_token
from passlib.context import CryptContext
from ..config import app_settings
from uuid import UUID
from datetime import timedelta
from app.worker.tasks import  send_email_with_template


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService):
    def __init__(self, model: type[User], session: AsyncSession):
       self.model = model
       self.session = session


    async def _add_user(self, data: dict, router_prefix: str) -> User:
        password = data.pop("password")
        user = self.model(
            **data,
            password_hash=password_context.hash(password)
        )

        user =  await self._add(user)
        token = generate_url_safe_token({
            "email": user.email,
            "id": str(user.id)
        })

        send_email_with_template.delay(
            recipients=[user.email],
            subject="Verify Your Account With FastShip",
            context={
                "username": user.name,
                "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
            },
            template_name="mail_email_verify.html"
        )
        return user


    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise InvalidToken()
        user = await self._get(UUID(token_data["id"]))
        user.email_verified = True
        await self._update(user)


    async def _get_by_email(self, email) -> User | None:
        return await self.session.scalar(select(self.model).where(self.model.email==email))

    async def _generate_token(self, email,password) -> str:
        user = await self._get_by_email(email)
        if user is None or not password_context.verify(password, user.password_hash):
            raise BadCredentials()

        if  not user.email_verified:
            raise ClientNotVerified()

        return  generate_access_token(data={
            "user": {"name": user.name, "id": str(user.id)}})


    async def send_password_reset_link(self, email, router_prefix: str):
       user = await self._get_by_email(email)
       token = generate_url_safe_token({"id": str(user.id)}, salt="password_reset")
       send_email_with_template.delay(
           recipients=[user.email],
           subject="FastShip Account Password Reset",
           context={
               "username": user.name,
               "reset_url": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset_password_form?token={token}"
           },
           template_name="mail_password_reset.html"
       )



    async def reset_password(self, token: str, password: str) -> bool:
        token_data = decode_url_safe_token(token, salt="password_reset",expiry=timedelta(days=1))
        if not token_data:
            return False
        user = await self._get(UUID(token_data["id"]))
        user.password_hash = password_context.hash(password)
        await self._update(user)
        return True





