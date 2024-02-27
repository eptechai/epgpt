from dataclasses import dataclass
from typing import Any

from llama_index.llms import (
    CompletionResponse,
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from llama_index.llms.base import llm_completion_callback
from transformers import Pipeline


@dataclass
class Config:
    """
    Config object for the LLM model
    """

    qe_k: int = 5
    qe_top_k: int = 5
    qe_temperature: float = 0.25
    qe_max_new_tokens: int = 250
    qe_score_threshold: float = 0.7
    qe_repetition_penalty: float = 1.2
    qe_reranker_top_n: int = 4
    qe_similarity_top_k: int = 12

    @classmethod
    def from_dict(cls, config):
        qe_k = int(config.get("qe_k", cls.qe_k))
        qe_top_k = int(config.get("qe_top_k", cls.qe_top_k))
        qe_temperature = float(config.get("qe_temperature", cls.qe_temperature))
        qe_max_new_tokens = int(config.get("qe_max_new_tokens", cls.qe_max_new_tokens))
        qe_score_threshold = float(
            config.get("qe_score_threshold", cls.qe_score_threshold)
        )
        qe_repetition_penalty = float(
            config.get("qe_repetition_penalty", cls.qe_repetition_penalty)
        )
        qe_reranker_top_n = int(config.get("qe_reranker_top_n", cls.qe_reranker_top_n))
        qe_similarity_top_k = int(
            config.get("qe_similarity_top_k", cls.qe_similarity_top_k)
        )

        obj = cls(
            qe_k,
            qe_top_k,
            qe_temperature,
            qe_max_new_tokens,
            qe_score_threshold,
            qe_repetition_penalty,
            qe_reranker_top_n,
            qe_similarity_top_k,
        )
        return obj

    @classmethod
    def from_proto(cls, config):
        extracted_config = {
            "qe_k": config.qe_k,
            "qe_top_k": config.qe_top_k,
            "qe_temperature": config.qe_temperature,
            "qe_max_new_tokens": config.qe_max_new_tokens,
            "qe_score_threshold": config.qe_score_threshold,
            "qe_repetition_penalty": config.qe_repetition_penalty,
            "qe_reranker_top_n": config.qe_reranker_top_n,
            "qe_similarity_top_k": config.qe_similarity_top_k,
        }

        return cls.from_dict(extracted_config)

    def to_dict(self):
        return self.__dict__

    def __post_init__(self) -> None:
        if not (1 <= self.qe_k <= 15):
            raise ValueError("k should belong to [1, 15]")

        if not (1 <= self.qe_top_k <= 25):
            raise ValueError("top_k should belong to [1, 25]")

        if not (0 <= self.qe_temperature <= 3):
            raise ValueError("temperature should belong to [0, 3]")

        if not (1 <= self.qe_max_new_tokens <= 500):
            raise ValueError("max_new_tokens should belong to [1, 500]")

        if not (0 <= self.qe_score_threshold <= 5):
            raise ValueError("score_threshold should belong to [0, 5]")

        if not (0 <= self.qe_reranker_top_n <= 10):
            raise ValueError("reranker_top_n should belong to [0, 10]")

        if not (0 <= self.qe_similarity_top_k <= 20):
            raise ValueError("similarity_top_k should belong to [0, 20]")


class Responder(CustomLLM):
    model: Pipeline = None
    max_tokens: int = 356
    context_window: int = 2048
    model_name: str = ""

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_tokens,
            model_name=self.model_name,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        prompt_length = len(prompt)
        response = self.model(prompt, max_new_tokens=self.max_tokens, max_length=100)[
            0
        ]["generated_text"]

        # only return newly generated tokens
        text = response[prompt_length:]
        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        raise NotImplementedError()
