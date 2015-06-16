"""
Create a model with the bare minimum: a PK and a value
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TestModel(Base):
    __tablename__ = 'test_model'

    id = Column(Integer, primary_key=True)
    value = Column(String)


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



"""
Insert some greenlet magic into generators
"""
from greenlet import greenlet


def greenletify_gen(mapping):
    """ This generator will be passed to bulk operations
        Greenlets allow us to get out of the bulk methods
        And thus run them concurrently """
    if mapping is None:
        raise StopIteration()
    yield mapping
    for mapping in iter(greenlet.getcurrent().parent.switch, None):
        yield mapping


"""
Run different tests
"""
from sqlalchemy.exc import ResourceClosedError


"""
First test
------------------------------------------------------
Send a value to the `bulk_insert` operation first
Then send one to the `bulk_update`
To finish end the `bulk_insert` then the `bulk_update`
------------------------------------------------------
Result: ResourceClosedError
"""
with session_ctx_mgr() as session:
    insert_greenlet = greenlet(lambda mapping: session.bulk_insert_mappings(TestModel, greenletify_gen(mapping)))
    update_greenlet = greenlet(lambda mapping: session.bulk_update_mappings(TestModel, greenletify_gen(mapping)))
    print('Start with an insert first.')
    insert_greenlet.switch({'id': 2, 'value': 2})
    update_greenlet.switch({'id': 1, 'value': 2})
    print('And end the bulk_insert first.')
    insert_greenlet.switch(None)
    try:
        update_greenlet.switch(None)
    except ResourceClosedError:
        print('This does not work.')
    else:
        session.commit()

"""
Second test
--------------------------------------------------------------------
Send a value to the `bulk_insert` operation first
Then send one to the `bulk_update`
But this time end the `bulk_update` first and then the `bulk_insert`
--------------------------------------------------------------------
Result: it works
"""
with session_ctx_mgr() as session:
    insert_greenlet = greenlet(lambda mapping: session.bulk_insert_mappings(TestModel, greenletify_gen(mapping)))
    update_greenlet = greenlet(lambda mapping: session.bulk_update_mappings(TestModel, greenletify_gen(mapping)))
    print('Start with an insert first.')
    insert_greenlet.switch({'id': 2, 'value': 2})
    update_greenlet.switch({'id': 1, 'value': 2})
    print('But end with the bulk_update first.')
    update_greenlet.switch(None)
    insert_greenlet.switch(None)
    session.commit()
    print('And it works.')

"""
Third test
------------------------------------------------------
Send a value to the `bulk_insert` operation first
Then send one to the `bulk_update`
Send other values to both operations
Send the last value to the `bulk_insert`
End the `bulk_update` first and then the `bulk_insert`
------------------------------------------------------
Result: it still works
"""
with session_ctx_mgr() as session:
    insert_greenlet = greenlet(lambda mapping: session.bulk_insert_mappings(TestModel, greenletify_gen(mapping)))
    update_greenlet = greenlet(lambda mapping: session.bulk_update_mappings(TestModel, greenletify_gen(mapping)))
    print('Start with an insert, do a bunch of things, end with an insert.')
    insert_greenlet.switch({'id': 3, 'value': 3})
    update_greenlet.switch({'id': 1, 'value': 3})
    insert_greenlet.switch({'id': 4, 'value': 4})
    update_greenlet.switch({'id': 2, 'value': 3})
    insert_greenlet.switch({'id': 5, 'value': 5})
    update_greenlet.switch(None)
    insert_greenlet.switch(None)
    session.commit()
    print('Still works, what counts is the first operation.')

"""
Conclusion:
What counts is to which operation is the first sent:
- if sent to the `bulk_insert`, the `bulk_update` has to finish first
- if sent to the `bulk_update`, the `bulk_insert` has to finish first
"""
