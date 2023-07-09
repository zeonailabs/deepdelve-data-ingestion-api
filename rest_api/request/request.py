from typing import Any, Collection, Dict, List, Optional, Union, Literal

from pydantic import BaseModel
from fastapi import Form


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


class MetaData(BaseModel):
    metaKey: str
    value: str


class Data(BaseModel):
    key: str
    value: str


class SurveyData(BaseModel):
    Id: str
    Data: List[Data]


class Survey(BaseModel):
    surveyId: str
    metaData: List[MetaData]
    surveyDescription: str
    surveyData: List[SurveyData]


class SurveyMeta(BaseModel):
    surveyId: str
    metaData: List[MetaData]


class DataSurvey(BaseModel):
    surveyId: str


class Organization(BaseModel):
    surveyList: List[Survey]


class OrganizationMeta(BaseModel):
    surveyList: List[SurveyMeta]


class OrganizationSurvey(BaseModel):
    surveyList: List[DataSurvey]
