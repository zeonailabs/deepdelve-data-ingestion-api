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
    # surv_table_id = Column(
    #     Integer,
    #     ForeignKey("summarygen_request.id", ondelete="CASCADE", onupdate="CASCADE"),
    #     nullable=False,
    #     index=True
    # )
    orgId = Column(String(256), nullable=False)
    surveyId = Column(String(256), nullable=False)
    metaKey = Column(String(1024), nullable=True)
    metaValue = Column(String(1024), nullable=True)
    __table_args__ = (
        ForeignKeyConstraint(
            [orgId, surveyId], [SurveyInsertRequest.orgId, SurveyInsertRequest.surveyId], ondelete="CASCADE", onupdate="CASCADE"
        ),
        {},
    )
