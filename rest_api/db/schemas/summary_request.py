from pydantic import BaseModel, HttpUrl

from typing import Sequence


class SummaryGenReqBase(BaseModel):
    org_id: str
    project_id: str
    doc_id: str

class SummaryGenReqCreate(SummaryGenReqBase):
    org_id: str
    project_id: str
    doc_id: str
    summary_type: str
    summary_length: int
    s3_path: str 


class SummaryGenReqUpdate(SummaryGenReqBase):
    org_id: str
    project_id: str
    doc_id: str
    s3_path: str = None
