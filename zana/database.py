import os

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ZanaEngineSession:
    __engine = None

    @classmethod
    def get_sessionmaker(cls):
        # Using sqlite for portability and fast mvp
        db_url = os.getenv("ZANA_DATABASE_URL")
        if not db_url:
            raise Exception("ZANA_DATABASE_URL undefined")
        if os.getenv("ZANA_TEST") and "test" not in db_url:
            raise Exception("ZANA_DATABASE_URL for ZANA_TEST does not contain substring test")

        if not cls.__engine:
            cls.__engine = create_engine(
                db_url,
                connect_args={"check_same_thread": False},

            )

            # Fix SERIALIZABLE for sqlite
            # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
            @event.listens_for(cls.__engine, "connect")
            def do_connect(dbapi_connection, connection_record):
                # disable pysqlite's emitting of the BEGIN statement entirely.
                # also stops it from emitting COMMIT before any DDL.
                dbapi_connection.isolation_level = None

            # Only set once when cls.__engine is created for the first time to avoid multiple listeners nesting BEGIN
            @event.listens_for(cls.__engine, "begin")
            def do_begin(conn):
                # emit our own BEGIN
                conn.exec_driver_sql("BEGIN")

            if os.getenv("ZANA_TEST"):
                #from alembic.command import upgrade as alembic_upgrade
                #from alembic.config import Config as AlembicConfig
                #alembic_config = AlembicConfig("./alembic.ini")
                #alembic_config.set_main_option('sqlalchemy.url', db_url) # set it again in case
                #alembic_upgrade(alembic_config, 'head')
                Base.metadata.bind = cls.__engine
                Base.metadata.create_all()

        return sessionmaker(autocommit=False, autoflush=False, bind=cls.__engine)()


