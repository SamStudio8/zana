# ZANA

### Install

#### Deps

```
pip install fastapi[all] uvicorn SQLAlchemy alembic pytest pytest-asyncio
```

#### Database

* `cp alembic.ini.example alembic.ini`
* `PYTHONPATH=. alembic upgrade head`

#### Development

* `PYTHONPATH=. alembic revision --autogenerate -m "comment"`

#### Ship it

```
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind $ZANA_HOST:$ZANA_PORT zana.server:app
```

#### Test

```
curl -X POST -H 'Content-type: application/json' --data '{"zeal": "TEST-12345", "pool": "TEST"}' 127.0.0.1:5077/add
requests.post("http://localhost:5077/add", json={"zeal": "TEST-09876", "pool": "TEST"})
```

```
curl -X POST -H 'Content-type: application/json' --data '{"org_code": "TEST", "prefix": "TEST", "linkage_id": "XYZ", "pool": "TEST"}' 127.0.0.1:5077/issue
requests.post("http://localhost:5077/issue", json={"org_code": "PROD", "prefix": "PROD", "linkage_id": "SECRET1", "pool": "TEST"})
```

```
curl -L 127.0.0.1:5077/size/TEST
requests.get("http://localhost:5077/size/TEST").json()
```
