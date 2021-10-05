import pytest
import os
os.environ["ZANA_TEST"] = '1'

from httpx import AsyncClient

from zana.server import get_application


@pytest.fixture(scope="session")
def test_app():
    return get_application()

@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(
        app=test_app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_hoot(test_app, test_client):
    res = await test_client.get(test_app.url_path_for("root"))
    assert res.status_code == 200
    assert res.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_add(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 200
    assert res.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_add2(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 200
    assert res.json() == {"message": "Hello World"}
