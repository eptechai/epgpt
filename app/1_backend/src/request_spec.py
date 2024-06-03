from typing import Optional

from pydantic import BaseModel, Field


class ParamsUpdateRequest(BaseModel):
    # TODO: Make the default values dynamic, i.e get the default values from the model

    qe_k: int = Field(default=3, ge=1, le=15, description="")
    qe_top_k: int = Field(default=5, ge=1, le=25, description="")
    qe_temperature: float = Field(default=0.25, ge=0, le=3, description="")
    qe_max_new_tokens: int = Field(default=200, ge=1, le=500, description="")
    qe_score_threshold: float = Field(default=0.8, ge=0, le=5, description="")
    qe_repetition_penalty: float = Field(default=1.2, ge=0, le=2.0, description="")
    qe_reranker_top_n: int = Field(default=4, ge=0, le=10, description="")
    qe_similarity_top_k: int = Field(default=12, ge=0, le=20, description="")

    rs_k: int = Field(default=3, ge=1, le=15, description="")
    rs_top_k: int = Field(default=5, ge=1, le=25, description="")
    rs_temperature: float = Field(default=0.25, ge=0, le=3, description="")
    rs_max_new_tokens: int = Field(default=200, ge=1, le=500, description="")
    rs_score_threshold: float = Field(default=0.8, ge=0, le=5, description="")
    rs_repetition_penalty: float = Field(default=1.2, ge=0, le=2.0, description="")

    use_only_uploaded: bool = Field(default=False, description="")


class MessageRequest(BaseModel):
    prompt: str


class MessageFeedback(BaseModel):
    is_feedback_positive: Optional[bool]


class CompanyRequest(BaseModel):
    name: str
    sub_sector: Optional[str] = None
    sub_sector_id: Optional[str] = None


class SubsectorRequest(BaseModel):
    name: str


class TagRequest(BaseModel):
    name: str
    company: str
    sub_sector: str
    year: int
