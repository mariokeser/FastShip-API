from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel
from fastapi import HTTPException, status


class BaseService:
    def __init__(self,model:type[SQLModel], session: AsyncSession):
        self.model=model
        self.session = session

    async def _get(self, id: UUID):
        entity =  await self.session.get(self.model, id)
        if not entity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Not found")
        return entity

    async def _add(self, entity: SQLModel):
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def _update(self, entity: SQLModel):
        return await self._add(entity)

    async def _delete(self, entity: SQLModel):
        await self.session.delete(entity)
        await self.session.commit()
