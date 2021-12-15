import pytest
import os
import datetime
import asyncio

# Turn on test database in ZanaEngineSession
os.environ["ZANA_TEST"] = '1'

from httpx import AsyncClient

from zana.server import get_application
from zana.database import ZanaEngineSession

@pytest.fixture(scope="session")
def test_db(tmpdir_factory):
    # https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
    # despite the warning we can get an in-memory database to work but the async tests
    # will fail, just use a test file instead
    tmp_db = str(tmpdir_factory.mktemp("scratch").join("mytest.db"))
    os.environ["ZANA_DATABASE_URL"] = "sqlite:///"+tmp_db

@pytest.fixture
def clear_test_data():
    db = ZanaEngineSession.get_sessionmaker()
    with db.begin():
        db.execute("DELETE FROM zealidentifier WHERE pool LIKE 'TEST%';")

@pytest.fixture(scope="session")
def test_app(test_db):
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
@pytest.mark.usefixtures("clear_test_data")
async def test_add(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 201
    reply = res.json()
    assert reply["pool"] == "TEST"
    assert reply["zeal"] == "HOOT-12345"
    assert reply["assigned_on"] is None
    assert reply["assigned_to"] is None
    assert reply["linkage_id"] is None
    assert reply["is_assigned"] is False
    assert reply["prefix"] is None
    assert reply["version"] == 0

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_add_two(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 201

    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12346", "pool": "TEST"})
    assert res.status_code == 201
    reply = res.json()
    assert reply["pool"] == "TEST"
    assert reply["zeal"] == "HOOT-12346"
    assert reply["assigned_on"] is None
    assert reply["assigned_to"] is None
    assert reply["linkage_id"] is None
    assert reply["is_assigned"] is False
    assert reply["prefix"] is None
    assert reply["version"] == 0

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_add_dup(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 201
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    assert res.status_code == 409
    reply = res.json()
    assert reply["zeal"] == "HOOT-12345"
    assert reply["message"] == "duplicate zeal"

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_add_empty(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={})
    assert res.status_code == 422

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TEST",
    })
    assert res.status_code == 201
    reply = res.json()
    assert datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert reply["assigned_to"] == "HOOT"
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f") != datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f")
    assert reply["is_assigned"] is True
    assert reply["linkage_id"] is None
    assert reply["pool"] == "TEST"
    assert reply["prefix"] == "MEOW"
    assert reply["version"] == 1
    assert reply["zeal"] == "HOOT-12345"

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_with_linkage(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TEST",
        "linkage_id": "12345",
    })
    assert res.status_code == 201
    reply = res.json()
    assert datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert reply["assigned_to"] == "HOOT"
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f") != datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f")
    assert reply["is_assigned"] is True
    assert reply["linkage_id"] == "12345"
    assert reply["pool"] == "TEST"
    assert reply["prefix"] == "MEOW"
    assert reply["version"] == 1
    assert reply["zeal"] == "HOOT-12345"

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_out_of_zeal(test_app, test_client):
    # Add no Zeal to pool so it is empty
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "TEST",
        "pool": "TEST",
    })
    assert res.status_code == 507
    assert res.json() == {"message": "out of zeal"}

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_out_of_zeal_pool(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST-NO"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "TEST",
        "pool": "TEST",
    })
    assert res.status_code == 507
    assert res.json() == {"message": "out of zeal"}

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_with_pooled_linkage(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TEST",
        "linkage_id": "12345",
    })
    assert res.status_code == 201

    # Make second request for issue
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TEST",
        "linkage_id": "12345",
    })
    assert res.status_code == 200
    reply = res.json()
    assert datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert reply["assigned_to"] == "HOOT"
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f").date() == datetime.date.today()
    assert datetime.datetime.strptime(reply["created_on"], "%Y-%m-%dT%H:%M:%S.%f") != datetime.datetime.strptime(reply["assigned_on"], "%Y-%m-%dT%H:%M:%S.%f")
    assert reply["is_assigned"] is True
    assert reply["linkage_id"] == "12345"
    assert reply["pool"] == "TEST"
    assert reply["prefix"] == "MEOW"
    assert reply["version"] == 1
    assert reply["zeal"] == "HOOT-12345"

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_with_unpooled_linkage(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345-A", "pool": "TESTA"})
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345-B", "pool": "TESTB"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TESTA",
        "linkage_id": "12345",
    })
    assert res.status_code == 201
    reply = res.json()
    assert reply["zeal"] == "HOOT-12345-A"
    assert reply["pool"] == "TESTA"

    # Make second request for issue
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TESTB",
        "linkage_id": "12345",
    })
    assert res.status_code == 201 # should create a new linkage
    reply = res.json()
    assert reply["zeal"] == "HOOT-12345-B"
    assert reply["pool"] == "TESTB"


@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_with_unpooled_linkage_and_empty_pool(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345-A", "pool": "TESTA"})
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TESTA",
        "linkage_id": "12345",
    })
    assert res.status_code == 201
    reply = res.json()
    assert reply["zeal"] == "HOOT-12345-A"
    assert reply["pool"] == "TESTA"

    # Make second request for issue
    res = await test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT",
        "prefix": "MEOW",
        "pool": "TESTB",
        "linkage_id": "12345",
    })
    assert res.status_code == 507 # should fail to make new linkage as the pool is depleted

@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_two_requests(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})

    t1 = asyncio.create_task(test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT1",
        "prefix": "TEST",
        "pool": "TEST",
        "linkage_id": 1,
    }))
    t2 = asyncio.create_task(test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT2",
        "prefix": "TEST",
        "pool": "TEST",
        "linkage_id": 2,
    }))
    await t1
    await t2
    codes = [t1.result().status_code, t2.result().status_code]
    assert 201 in codes
    assert 507 in codes

    replies = [t1.result().json(), t2.result().json()]

    if len(replies[0]) > len(replies[1]):
        one_won = True
        bad, good = replies[1], replies[0]
    else:
        one_won = False
        bad, good = replies[0], replies[1]

    assert bad == {"message": "out of zeal"}

    if one_won:
        assert good["linkage_id"] == "1"
        assert good["assigned_to"] == "HOOT1"
    else:
        assert good["linkage_id"] == "2"
        assert good["assigned_to"] == "HOOT2"

    assert good["prefix"] == "TEST"
    assert good["zeal"] == "HOOT-12345"


@pytest.mark.asyncio
@pytest.mark.usefixtures("clear_test_data")
async def test_issue_two_requests(test_app, test_client):
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-12345", "pool": "TEST"})
    res = await test_client.post(test_app.url_path_for("add_identifier"), json={"zeal": "HOOT-67890", "pool": "TEST"})

    t1 = asyncio.create_task(test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT1",
        "prefix": "TEST",
        "pool": "TEST",
        "linkage_id": 1,
    }))
    t2 = asyncio.create_task(test_client.post(test_app.url_path_for("issue_identifier"), json={
        "org_code": "HOOT2",
        "prefix": "TEST",
        "pool": "TEST",
        "linkage_id": 2,
    }))
    await t1
    await t2
    codes = [t1.result().status_code, t2.result().status_code]
    assert codes == [201, 201]

    replies = [t1.result().json(), t2.result().json()]
    assert {"message": "out of zeal"} not in replies

    assert replies[0]["assigned_to"] == "HOOT1"
    assert replies[0]["linkage_id"] == "1"
    assert replies[1]["assigned_to"] == "HOOT2"
    assert replies[1]["linkage_id"] == "2"

    if replies[0]["zeal"] == "HOOT-12345":
        assert replies[1]["zeal"] == "HOOT-67890"
    elif replies[0]["zeal"] == "HOOT-67890":
        assert replies[1]["zeal"] == "HOOT-12345"

