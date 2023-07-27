from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rest_api.db.db_config import SQLALCHEMY_DATABASE_URI
from rest_api.db.models.base import ORMBase
from sqlalchemy.orm import scoped_session


def SessionLocal():
    """

    :return:
    """
    engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_recycle=1600, pool_pre_ping=True)
    ORMBase.metadata.create_all(engine)
    return scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
