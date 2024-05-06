from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from response_synthesizer import Config, ResponseSynthesizer


from models.response_synthesizer import QueryRequest, QueryResponse

RESPONSE_SYNTHESIZER_TAG = "response_synthesyzer"

def init_response_synthesizer_router():
    """
    Price conversion router which holds endpoints to return a price data from database
    """
    response_synthesizer_router = APIRouter()

    response_synthesyzer_service = ResponseSynthesizer()

    @response_synthesizer_router.get(
        "/response/chat/{conversion_id}",
        response_model=QueryResponse,
        tags=[RESPONSE_SYNTHESIZER_TAG],
    )
    async def synthesize(
        conversion_id: str,
        query_request: QueryRequest = Depends(),
      
    ):
        query = query_request.query
        qa_pairs = zip(query_request.question, query_request.answers)
        response = response_synthesyzer_service.initialize_synthesizer(query, qa_pairs)
        
        return QueryResponse(conversation_id=conversion_id, response=response.response)
    
    return response_synthesizer_router