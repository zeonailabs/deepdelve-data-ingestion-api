from pydantic import BaseModel, HttpUrl
from typing import List, Dict
from typing import Optional


class SurvInsReqCreate(BaseModel):
    orgId: str
    surveyId: str
    surveyDescription: Optional[str] = None
    s3_file_path: Optional[str] = None


class SurvMetaInsReqCreate(BaseModel):
    surveyReqId: int
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None


class SurvUpReqCreate(BaseModel):
    orgId: str
    surveyId: str
    surveyDescription: Optional[str] = None
    s3_file_path: Optional[str] = None


class SurvMetaUpReqCreate(BaseModel):
    surveyReqId: int
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None
