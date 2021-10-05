import os

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_sessionmaker():
    # Using sqlite for portability and fast mvp

    if os.getenv("ZANA_TEST"):
        # https://gehrcke.de/2015/05/in-memory-sqlite-database-and-flask-a-threading-trap/
        db_url = "sqlite:///test.db"
        os.environ["ZANA_DATABASE_URL"] = db_url
        from alembic.command import upgrade as alembic_upgrade
        from alembic.config import Config as AlembicConfig
        alembic_config = AlembicConfig("./alembic.ini")
        alembic_config.set_main_option('sqlalchemy.url', db_url) # set it again in case
        alembic_upgrade(alembic_config, 'head')
        #Base.metadata.bind = engine
        #Base.metadata.create_all()
    else:
        db_url = os.getenv("ZANA_DATABASE_URL")
        if not db_url:
            raise Exception("ZANA_DATABASE_URL undefined")

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},

    )

    # Fix SERIALIZABLE for sqlite
    # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        # emit our own BEGIN
        conn.exec_driver_sql("BEGIN")

    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()
