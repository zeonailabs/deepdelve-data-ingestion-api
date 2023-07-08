from sqlalchemy import and_, func, create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ORMBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    #created = Column(DateTime, server_default=func.now())
    #updated = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
