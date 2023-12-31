from email import message
from os import stat
from tokenize import Double
from typing import Any, Dict, List, Optional
from numpy import double

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class StatusObj(BaseModel):
    success: bool
    code: int


class InsertAPIResponse(BaseModel):
    status: StatusObj
    message: str
    successSurveyIds: List[Dict]
    failedSurveyIds: List[Dict]


class UpdateAPIResponse(BaseModel):
    status: StatusObj
    message: str
    successSurveyIds: List[Dict]
    failedSurveyIds: List[Dict]


class DeleteAPIResponse(BaseModel):
    status: StatusObj
    message: str
    successSurveyIds: List[Dict]
    failedSurveyIds: List[Dict]

class SearchAPIResponse(BaseModel):
    status : StatusObj
    answer : str
    surveyList : List[Dict]

class StatusAPIResponse(BaseModel):
    status : StatusObj
    dataPresent : bool
    surveyData : Dict

class FeedbackAPIResponse(BaseModel):
    status: StatusObj
    message: str