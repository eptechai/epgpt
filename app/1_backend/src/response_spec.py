import uuid
from typing import List, Optional

from pydantic import BaseModel


class Subquestion(BaseModel):
    id: uuid.UUID
    text: str
    response: str
    tool_name: str


class SubquestionListResponse(BaseModel):
    subquestions: List[Subquestion]


class Conversation(BaseModel):
    id: uuid.UUID
    title: str


class ConversationResponse(BaseModel):
    conversation_id: uuid.UUID


class CompanyResponse(BaseModel):
    id: uuid.UUID
    name: str
    sub_sector_id: uuid.UUID


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]


class SubsectorResponse(BaseModel):
    id: uuid.UUID
    name: str
    companies: List[CompanyResponse]


class SubsectorListResponse(BaseModel):
    subsectors: List[SubsectorResponse]


class ConversationListResponse(BaseModel):
    next_cursor: int
    conversations: List[Conversation]


class ParamsResponse(BaseModel):
    qe_k: int
    qe_top_k: int
    qe_temperature: float
    qe_max_new_tokens: int
    qe_score_threshold: float
    qe_repetition_penalty: float
    qe_reranker_top_n: int
    qe_similarity_top_k: int
    rs_k: int
    rs_top_k: int
    rs_temperature: float
    rs_max_new_tokens: int
    rs_score_threshold: float
    rs_repetition_penalty: float

    use_only_uploaded: bool


class CitationResponse(BaseModel):
    id: uuid.UUID
    content: str
    pageNumber: int
    fileName: str
    documentId: uuid.UUID


class CitationListResponse(BaseModel):
    citations: List[CitationResponse]


class MessageResponse(BaseModel):
    id: uuid.UUID
    author: str
    text: str
    conversationId: uuid.UUID
    citations: List[CitationResponse]
    isFeedbackPositive: Optional[bool]


class MessageListResponse(BaseModel):
    next_cursor: int
    messages: List[MessageResponse]


class AttachmentStatus(BaseModel):
    id: uuid.UUID
    name: str
    status: str


class AttachmentListResponse(BaseModel):
    attachments: List[AttachmentStatus]
