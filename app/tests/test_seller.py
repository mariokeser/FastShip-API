from httpx import AsyncClient
from app.tests import example


async def test_seller_login(client: AsyncClient):
    response = await client.post("/seller/token",
                      data={"grant_type": "password",
                          "username": example.SELLER["email"],
                            "password": example.SELLER["password"]})
    assert response.status_code == 200
    assert "access_token" in response.json()