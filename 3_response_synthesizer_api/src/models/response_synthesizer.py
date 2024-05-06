from datetime import datetime
from typing import Dict, List, Optional
from fastapi import Query

from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str
    question: List[str] = Field(Query([]))
    answers: List[str] =  Field(Query([]))

class QueryResponse(BaseModel):
    conversation_id: str
    response: str
