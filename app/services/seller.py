from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.seller import SellerCreate
from ..database.models import Seller
from .user import UserService
from typing import cast


class SellerService(UserService):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Seller, session=session)

    async def add(self,seller_create: SellerCreate) -> Seller:
       seller =   await self._add_user(seller_create.model_dump(), "seller" )
       return  cast(Seller, seller)


    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)






