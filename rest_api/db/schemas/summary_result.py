from pydantic import BaseModel, HttpUrl

from typing import Sequence


class SummaryGenResultBase(BaseModel):
    req_id: str
    section_id: str
    section_name: str = None
    summary_output: str = None
    status: bool = False


class SummaryGenResultCreate(SummaryGenResultBase):
    req_id: str
    section_id: str
    section_name: str = None


class SummaryGenResultUpdate(SummaryGenResultBase):
    summary_output: str = None
    status: bool = False