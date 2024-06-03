from typing import Any

import torch
from llama_index import ServiceContext, get_response_synthesizer
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import (
    CompletionResponse,
    CompletionResponseGen,
    CustomLLM,
    LLMMetadata,
)
from llama_index.llms.base import llm_completion_callback
from llama_index.prompts.base import PromptTemplate
from llama_index.prompts.prompt_type import PromptType
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)

CONTEXT_WINDOW = 2048
MAX_TOKENS = 356
MODEL_ID = "HuggingFaceH4/zephyr-7b-beta"
TEMPERATURE = 0.05
TEXT_FINAL_PROMPT_TMPL = "{context_str}" "---" "{query_str}"
TEXT_FINAL_PROMPT = PromptTemplate(
    TEXT_FINAL_PROMPT_TMPL, prompt_type=PromptType.QUESTION_ANSWER
)
BNB_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)
MODEL = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    trust_remote_code=True,
    quantization_config=BNB_CONFIG,
    device_map="auto",
)
MODEL_PIPELINE = pipeline(
    "text-generation",
    model=MODEL,
    tokenizer=AutoTokenizer.from_pretrained(MODEL_ID),
    use_cache=True,
    device_map="auto",
    top_k=2,
    repetition_penalty=1.2,
    max_new_tokens=100,
    do_sample=True,
    temperature=TEMPERATURE,
    num_return_sequences=1,
)


class ResponseSynthesizerModel(CustomLLM):
    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=CONTEXT_WINDOW,
            num_output=MAX_TOKENS,
            model_name=MODEL_ID,
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
        prompt = MODEL_PIPELINE.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=True
        )
        prompt_length = len(prompt)
        response = MODEL_PIPELINE(prompt, max_new_tokens=MAX_TOKENS)[0][
            "generated_text"
        ]

        # only return newly generated tokens
        text = response[prompt_length:]
        return CompletionResponse(text=text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        raise NotImplementedError()


def load_response_synthesizer():
    # callback manager
    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_handler = OpenInferenceCallbackHandler()
    callback_manager = CallbackManager([llama_debug, callback_handler])
    # embed_model
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en")
    # llm model

    # service context
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=ResponseSynthesizerModel(),
        callback_manager=callback_manager,
    )
    # response symthesizer
    model = get_response_synthesizer(
        response_mode="simple_summarize",
        text_qa_template=TEXT_FINAL_PROMPT,
        service_context=service_context,
    )
    return model
