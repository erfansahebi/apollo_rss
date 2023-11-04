import pytest
import uuid
from nameko.testing.services import worker_factory
from apollo_shared.alembic.models import Base
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects import postgresql
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope='session')
def db_url():
    return 'sqlite:///:memory:'


@pytest.yield_fixture(scope='session')
def db_connection(db_url, model_base, db_engine_options):
    engine = create_engine(db_url, **db_engine_options)
    model_base.metadata.create_all(engine)

    from rss.models import bookmark, comment, feed, rss

    rss.rsses.drop(engine)
    rss.rsses.create(engine)

    rss.rss_user.drop(engine)
    rss.rss_user.create(engine)

    feed.feeds.drop(engine)
    feed.feeds.create(engine)

    comment.comments.drop(engine)
    comment.comments.create(engine)

    bookmark.bookmarks.drop(engine)
    bookmark.bookmarks.create(engine)

    connection = engine.connect()
    model_base.metadata.bind = engine

    yield connection

    engine.dispose()


@pytest.fixture(scope='session')
def model_base():
    return Base


@pytest.fixture(scope='session')
def db_engine_options():
    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()

    @compiles(postgresql.UUID, 'sqlite')
    def compile_sqlite_uuid(type_, compiler, **kw):
        return 'STRING'

    return {}


@pytest.fixture
def context():
    return {
        'request_id': 'request_id',
        'token': 'token',
        'user_id': uuid.UUID("c4d4a094-e238-437a-9584-e8d612b5f85d"),
    }


@pytest.fixture
def rss_controller(database):
    from rss.controller import RssController
    return worker_factory(RssController, db=database)
