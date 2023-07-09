from sqlalchemy import Column, String, Text, Index
from sqlalchemy.orm import relationship

from rest_api.db.models.base import ORMBase


class SurveyInsertRequest(ORMBase):
    __tablename__ = "surveyData"

    orgId = Column(String(256), nullable=False)
    surveyId = Column(String(256), nullable=False)
    s3_file_path = Column(String(1024), nullable=True)
    surveyDescription = Column(String(1024), nullable=True)


class SurveyMetaInsertRequest(ORMBase):
    __tablename__ = "surveyMetaData"

    orgId = Column(String(256), nullable=False)
    surveyId = Column(String(256), nullable=False)
    metaKey = Column(String(1024), nullable=True)
    metaValue = Column(String(1024), nullable=True)
