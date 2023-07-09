from pydantic import BaseModel, HttpUrl
from typing import List, Dict
from typing import Optional


class SurvInsReqBase(BaseModel):
    orgId: str
    surveyId: str

class SurvInsReqCreate(SurvInsReqBase):
    orgId: str
    surveyId: str
    surveyDescription: Optional[str] = None
    s3_file_path: Optional[str] = None
    
class SurvMetaInsReqCreate(SurvInsReqBase):
    orgId: str
    surveyId: str
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None

class SurvUpReqCreate(SurvInsReqBase):
    orgId: str
    surveyId: str
    surveyDescription: Optional[str] = None
    s3_file_path: Optional[str] = None
    
class SurvMetaUpReqCreate(SurvInsReqBase):
    orgId: str
    surveyId: str
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None

