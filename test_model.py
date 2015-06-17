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
