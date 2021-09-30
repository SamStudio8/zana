# ZANA

### Install

#### Deps

```
pip install fastapi[all] uvicorn SQLAlchemy alembic
```

#### Database

* `cp alembic.ini.example alembic.ini`
* `PYTHONPATH=. alembic upgrade head`

#### Development

* `PYTHONPATH=. alembic revision --autogenerate -m "comment"`

#### Ship it

```
uvicorn main:app --reload --port $ZANA_PORT
```
