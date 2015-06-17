"""
Wrap the session management in a context manager
"""
import os
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


@contextmanager
def session_ctx_mgr():
    db_addr, db_port = os.getenv('DB_PORT_5432_TCP_ADDR'), os.getenv('DB_PORT_5432_TCP_PORT')
    db_uri = 'postgresql://postgres@%s:%s/postgres' % (db_addr, db_port)
    session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=create_engine(db_uri, convert_unicode=True),
    ))
    yield session
    session.close()
