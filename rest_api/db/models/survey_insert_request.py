from sqlalchemy import Column, String, Text, Index, Integer, ForeignKey, ForeignKeyConstraint, Enum
from sqlalchemy.orm import relationship
import enum
from rest_api.db.models.base import ORMBase


class SurveyInsertRequest(ORMBase):
    __tablename__ = "surveyData"
    orgId = Column(String(256), nullable=False)
    surveyId = Column(String(256), nullable=False)
    s3_file_path = Column(String(1024), nullable=True)
    surveyDescription = Column(String(1024), nullable=True)
    total_no_of_rows = Column(Integer, nullable=True, default=0)
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


class SurveySearchInsertRequest(ORMBase):
    __tablename__ = "surveySearchData"
    searchId = Column(String(256), nullable=False)
    orgId = Column(String(256), nullable=False)
    question = Column(String(1024), nullable=True)
    answer = Column(String(1024), nullable=True)
    inputSurveyIdList = Column(String(256), nullable=False)
    filters = Column(String(1024), nullable=True)
    filteredSurveyIdList = Column(String(256), nullable=False)
    modelParameter = Column(String(1024), nullable=True)
    calculationDescription = Column(String(1024), nullable=True)
    survey_search_request = relationship(
        "SurveyFeedbackInsertRequest",
        cascade="all,delete-orphan",
        lazy="joined",
        uselist=True,
    )


class feedback(enum.Enum):
    like = "like"
    dislike = "dislike"


class options(enum.Enum):
    accurate = "Accurate Information"
    time_save = "Time Saving"
    genuine = "Genuine Resource"
    inaccurate = "Inaccurate Information"
    not_help = "Not helpful"


class SurveyFeedbackInsertRequest(ORMBase):
    __tablename__ = "surveyFeedbackData"
    searchReqId = Column(
        Integer,
        ForeignKey("surveySearchData.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True
    )
    searchId = Column(String(256), nullable=False)
    # feedback = Column(Enum(feedback), nullable=False)
    # option = Column(Enum(options), nullable=True)
    feedback = Column(Enum("like", "dislike"), nullable=False)
    option = Column(
        Enum("Accurate Information", "Time Saving", "Genuine Resource", "Inaccurate Information", "Not helpful"),
        nullable=True, default="Accurate Information")
    remarks = Column(String(1024), nullable=True)
