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

    rs_k: int = 5
    rs_top_k: int = 5
    rs_temperature: float = 0.25
    rs_max_new_tokens: int = 250
    rs_score_threshold: float = 0.7
    rs_repetition_penalty: float = 1.2

    @classmethod
    def from_dict(cls, config):
        rs_k = int(config.get("rs_k", cls.rs_k))
        rs_top_k = int(config.get("rs_top_k", cls.rs_top_k))
        rs_temperature = float(config.get("rs_temperature", cls.rs_temperature))
        rs_max_new_tokens = int(config.get("rs_max_new_tokens", cls.rs_max_new_tokens))
        rs_score_threshold = float(
            config.get("rs_score_threshold", cls.rs_score_threshold)
        )

        rs_repetition_penalty = float(
            config.get("rs_repetition_penalty", cls.rs_repetition_penalty)
        )

        obj = cls(
            rs_k,
            rs_top_k,
            rs_temperature,
            rs_max_new_tokens,
            rs_score_threshold,
            rs_repetition_penalty,
        )
        return obj

    @classmethod
    def from_proto(cls, config):
        extracted_config = {
            "rs_k": config.rs_k,
            "rs_top_k": config.rs_top_k,
            "rs_temperature": config.rs_temperature,
            "rs_max_new_tokens": config.rs_max_new_tokens,
            "rs_score_threshold": config.rs_score_threshold,
            "rs_repetition_penalty": config.rs_repetition_penalty,
        }

        return cls.from_dict(extracted_config)

    def to_dict(self):
        return self.__dict__

    def __post_init__(self) -> None:
        if not (1 <= self.rs_k <= 15):
            raise ValueError("k should belong to [1, 15]")

        if not (1 <= self.rs_top_k <= 25):
            raise ValueError("top_k should belong to [1, 25]")

        if not (0 <= self.rs_temperature <= 3):
            raise ValueError("temperature should belong to [0, 3]")

        if not (1 <= self.rs_max_new_tokens <= 500):
            raise ValueError("max_new_tokens should belong to [1, 500]")

        if not (0 <= self.rs_score_threshold <= 5):
            raise ValueError("score_threshold should belong to [0, 5]")


class Summarizer(CustomLLM):
    model: Pipeline = None
    max_tokens: int = 100
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
        context = prompt.split("---")[0]
        query = prompt.split("---")[-1]
        message = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant condensing information that your team has separately researched into one final response. "
                    "You will be given sub questions and their corresponding answers along with the initial question that requires a response. "
                    "Only reference the information provided in your team's answers and no previous knowledge.\n"
                    "Your task is to combine the answers into a single cohesive response. IGNORE THE SUB QUESTIONS. "
                    "Ensure the final response maintains logical order, coherence, and full sentence structure. "
                    "Smoothly transition between points, using appropriate connective language to ensure the text reads as if it were addressing a single, unified question."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\nCombine the answers into a single cohesive response strictly using only "
                    "the information provided in the sub questions and not referencing the sub questions themselves to "
                    f"respond to the following question: {query}\n"
                ),
            },
        ]
        prompt = self.model.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=True
        )
        prompt_length = len(prompt)
        response = self.model(prompt, max_new_tokens=self.max_tokens)[0][
            "generated_text"
        ]

        # only return newly generated tokens
        text = response[prompt_length:]
        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        context = prompt.split("---")[0]
        query = prompt.split("---")[-1]
        message = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant condensing information that your team has separately researched into one final response. "
                    "You will be given sub questions and their corresponding answers along with the initial question that requires a response. "
                    "Only reference the information provided in your team's answers and no previous knowledge.\n"
                    "Your task is to combine the answers into a single cohesive response. IGNORE THE SUB QUESTIONS. "
                    "Ensure the final response maintains logical order, coherence, and full sentence structure. "
                    "Smoothly transition between points, using appropriate connective language to ensure the text reads as if it were addressing a single, unified question."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\nCombine the answers into a single cohesive response strictly using only "
                    "the information provided in the sub questions and not referencing the sub questions themselves to "
                    f"respond to the following question: {query}\n"
                ),
            },
        ]
        prompt = self.model.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=True
        )
        prompt_length = len(prompt)
        response = self.model(prompt, max_new_tokens=self.max_tokens)[0][
            "generated_text"
        ]

        # only return newly generated tokens
        text = response[prompt_length:]
        return CompletionResponse(text=text)
