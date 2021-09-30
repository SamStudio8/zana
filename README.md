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

* `PYTHONPATH=. alembic revision --autogenerate`

#### Ship it

```
uvicorn main:app --reload
```
