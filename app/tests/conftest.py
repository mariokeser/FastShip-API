import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database.session import get_session
from sqlmodel import SQLModel
from app.main import app
from app.tests import example


engine = create_async_engine(
    url="sqlite+aiosqlite:///:memory:"
)

test_session = async_sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=engine)

async def get_session_override():
    async with test_session() as session:
        yield session



@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test"
    ) as client:
        yield client



@pytest_asyncio.fixture(scope="session")
async def seller_token(client: AsyncClient, setup_and_teardown: None):
    response = await client.post("/seller/token",
                      data={"grant_type": "password",
                          "username": example.SELLER["email"],
                            "password": example.SELLER["password"]})
    assert "access_token" in response.json()
    return response.json()["access_token"]



@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown():
    print("starting tests")

    app.dependency_overrides[get_session] = get_session_override

    async with engine.begin() as connection:
        from app.database.models import DeliveryPartner, Seller, Shipment
        await connection.run_sync(SQLModel.metadata.create_all)
    async with test_session() as session:
        await example.create_test_data(session=session)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)

    app.dependency_overrides.clear()

    print("finished...")


@pytest_asyncio.fixture(scope="function")
async def db_session_rollback():
    async with test_session() as session:
        yield session
        await session.rollback()