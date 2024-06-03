from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse

from services.response_synthesizer_service import Config, ResponseSynthesizer


from models.response_synthesizer_models import QueryRequest, QueryResponse

RESPONSE_SYNTHESIZER_TAG = "response_synthesyzer"

def init_response_synthesizer_router():
    """
    Price conversion router which holds endpoints to return a price data from database
    """
    response_synthesizer_router = APIRouter()

    response_synthesyzer_service = ResponseSynthesizer()

    @response_synthesizer_router.get(
        "/response/chat/{conversation_id}",
        response_model=QueryResponse,
        tags=[RESPONSE_SYNTHESIZER_TAG],
    )
    async def synthesize(
        conversation_id: str,
        query_request: QueryRequest = Depends(),
      
    ):
        query = query_request.query
        qa_pairs = zip(query_request.question, query_request.answers)
        use_rag = query_request.store
        response = response_synthesyzer_service.initialize_synthesizer(query, qa_pairs, use_rag)
        
        return QueryResponse(conversation_id=conversation_id, response=response)
    
    return response_synthesizer_router