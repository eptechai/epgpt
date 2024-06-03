from typing import List, Annotated
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from services.lead_generator_service import LeadGenerator

from models.lead_generator_models import ProposalRequest, ProposalResponse, JobPostingRequest, JobPostingResponse, ProjectInfo, JobPostingInfo, ClientInformation

lead_generator_TAG = "lead_generator"

def init_lead_generator_router():
    """
    Price conversion router which holds endpoints to return a price data from database
    """
    lead_generator_router = APIRouter(
        prefix="/leads",
        tags=[lead_generator_TAG])

    lead_generator_service = LeadGenerator()

    @lead_generator_router.post(
        "/description/{conversation_id}",
        response_model=JobPostingResponse
    )
    async def describe(
        conversation_id: str,
        job_posting_request: JobPostingRequest,
      
    ):
        job_posting = job_posting_request.job_posting
        
        response = lead_generator_service.initialize_generate_job_desciption(job_posting)
        parsed_job_description = json.loads(response)
        parsed_job_description
        job_posting_dict = parsed_job_description["project_information"]
        print(parsed_job_description["client_information"])
        project_info = ProjectInfo(
            **job_posting_dict
        )
        client_info = ClientInformation(**parsed_job_description["client_information"])

        job_posting_info = JobPostingInfo(client_information=client_info, project_information=project_info)
        
        return JobPostingResponse(conversation_id=conversation_id, job_posting=job_posting_info)
    
    @lead_generator_router.post(
        "/proposal/{conversation_id}"
    )
    async def propose(
        conversation_id: str,
        proposal_request: ProposalRequest,
      
    ):
    
        job_description = proposal_request.job_description
        proposal_requirements = proposal_request.proposal_requirements
        selection_criteria = proposal_request.selection_criteria
        timeline = proposal_request.total_project_duration
        deliverables = proposal_request.deliverables
        response = lead_generator_service.generate_proposal(
            job_description,
            proposal_requirements,
            timeline,
            selection_criteria,
            deliverables,
        )
        
        
        return json.loads(response)
    
    return lead_generator_router