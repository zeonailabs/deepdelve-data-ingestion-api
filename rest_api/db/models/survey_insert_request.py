from sqlalchemy import Column, String, Text, Index, Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from rest_api.db.models.base import ORMBase


class SurveyInsertRequest(ORMBase):
    __tablename__ = "surveyData"
    orgId = Column(String(256), nullable=False)
    surveyId = Column(String(256), nullable=False)
    s3_file_path = Column(String(1024), nullable=True)
    surveyDescription = Column(String(1024), nullable=True)
    survey_data_request = relationship(
        "SurveyMetaInsertRequest",
        cascade="all,delete-orphan",
        lazy="joined",
        uselist=True,
    )


class SurveyMetaInsertRequest(ORMBase):
    __tablename__ = "surveyMetaData"
    surveyReqId = Column(
         Integer,
         ForeignKey("surveyData.id", ondelete="CASCADE", onupdate="CASCADE"),
         nullable=False,
         index=True
    )
    metaKey = Column(String(1024), nullable=True)
    metaValue = Column(String(1024), nullable=True)

