from pydantic import BaseModel, HttpUrl
from typing import List, Dict
from typing import Optional


class SurvInsReqCreate(BaseModel):
    orgId: str
    surveyId: str
    surveyDescription: Optional[str] = None
    s3_file_path: Optional[str] = None
    total_no_of_rows : int = 0


class SurvMetaInsReqCreate(BaseModel):
    surveyReqId: int
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None

class SurvSearchInsReqCreate(BaseModel):
    searchId : str
    orgId: str
    question: str
    answer: Optional[str] = None
    inputSurveyIdList : Optional[str] = None
    filters : Optional[str]
    filteredSurveyIdList: Optional[str] = None
    modelParameter : Optional[str] = None
    calculationDescription : Optional[str] = None

class SurvFeedInsReqCreate(BaseModel):
    searchReqId: int
    searchId : str
    feedback: Optional[str] = None
    option : Optional[str] = None
    remarks : str = None

class SurvFeedUpReqCreate(BaseModel):
    feedback: Optional[str] = None
    option : Optional[str] = None
    remarks : str = None

class SurvUpReqCreate(BaseModel):
    # orgId: str
    # surveyId: str
    # surveyDescription: Optional[str] = None
    # s3_file_path: Optional[str] = None
    total_no_of_rows : int = 0


class SurvMetaUpReqCreate(BaseModel):
    surveyReqId: int
    metaKey: Optional[str] = None
    metaValue: Optional[str] = None

class SurvSearchUpReqCreate(BaseModel):
    # searchId : str
    # orgId: str
    # question: str
    answer: Optional[str] = None
    # inputSurveyIdList : Optional[str] = None
    # filters : Optional[str]
    # filteredSurveyIdList: Optional[str] = None
    # modelParameter : Optional[str] = None
    calculationDescription : Optional[str] = None

