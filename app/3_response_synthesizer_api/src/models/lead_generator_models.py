from datetime import datetime
from typing import Dict, List, Optional
from fastapi import Query

from pydantic import BaseModel, Field

class JobPostingRequest(BaseModel):
    username: str
    user_id: str
    job_posting: str
    service: str

class ClientInformation(BaseModel):
    payment_method: str | None
    rating: str | int | None
    location: str | None
    local_time: str | None
    number_of_jobs_posted: str | int | None
    hire_rate: str | int | None
    open_jobs: str | int | None
    total_amount_spent: str | None
    number_of_hires: str | int | None
    active_hires: str | int | None
    industry: str | None
    membership_since: str | None


class ProjectInfo(BaseModel):
    project_name: str
    job_description: str
    objectives: List[str] = []
    technical_requirements: Dict[str,List[str]]
    deliverables: List[str]
    total_project_duration: str
    selection_criteria: List[str]
    proposal_requirements: List[str] 
    job_information: dict

class JobPostingInfo(BaseModel):
    client_information: ClientInformation
    project_information: ProjectInfo


class JobPostingResponse(BaseModel):
    conversation_id: str
    job_posting: JobPostingInfo


class ProposalRequest(BaseModel):
    job_description: str
    deliverables: List[str] = Field(Query([]))
    total_project_duration: str
    selection_criteria: List[str] =  Field(Query([]))
    proposal_requirements: List[str] = Field(Query([]))


class ProposalResponse(BaseModel):
    conversation_id: str
    response: str