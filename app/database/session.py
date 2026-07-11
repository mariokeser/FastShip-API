from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from app.config import db_settings

engine = create_async_engine(
    url=db_settings.POSTGRES_URL,
    echo=True
)





async_session = async_sessionmaker(
        class_=AsyncSession,
        expire_on_commit=False,
        bind=engine)

async def get_session():
    async with async_session() as session:
        yield session


