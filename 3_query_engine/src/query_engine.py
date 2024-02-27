from typing import List, Optional

import variables as vars
from llama_index import (
    ServiceContext,
    get_response_synthesizer,
)
from llama_index.bridge.pydantic import BaseModel, Field
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.indices.postprocessor import SentenceTransformerRerank
from llama_index.indices.vector_store.retrievers import (
    VectorIndexAutoRetriever,
)
from llama_index.llms import OpenAI
from llama_index.prompts.base import PromptTemplate
from llama_index.prompts.prompt_type import PromptType
from llama_index.query_engine.retriever_query_engine import (
    RetrieverQueryEngine,
)
from llama_index.question_gen.types import SubQuestion
from llama_index.schema import NodeWithScore
from llama_index.vector_stores.types import MetadataInfo, VectorStoreInfo
from llm_utils import Config, Responder
from logger import create_logger
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)

_logger = create_logger("query_engine:model")


class SubQuestionAnswerPair(BaseModel):
    """
    Pair of the sub question and optionally its answer (if its been answered yet).
    """

    sub_q: SubQuestion
    answer: Optional[str] = None
    sources: List[NodeWithScore] = Field(default_factory=list)


class QueryEngine(object):
    def __init__(self) -> None:
        self.params = Config()
        self.context_length = vars.CONTEXT_WINDOW

        with open("prompt.txt") as file:  # promp template
            prompt_template = file.read()

        self.prompt_template = PromptTemplate(
            prompt_template, prompt_type=PromptType.QUESTION_ANSWER
        )

        llama_debug = LlamaDebugHandler(print_trace_on_end=True)  # callback_manager
        callback_handler = OpenInferenceCallbackHandler()
        self.callback_manager = CallbackManager([llama_debug, callback_handler])
        self.embed_model = HuggingFaceEmbedding(model_name=vars.EMBEDDING_MODEL)
        self.tokenizer = AutoTokenizer.from_pretrained(vars.MODEL_ID)
        self.index_llm_model = OpenAI(
            model=vars.INDEXING_EMBEDDING_MODEL,
            temperature=0,
        )
        self.llm = AutoModelForCausalLM.from_pretrained(
            vars.MODEL_ID,
            trust_remote_code=True,
            quantization_config=vars.BNB_CONFIG,
            device_map="auto",
        )
        if vars.PEFT_MODEL is not None:
            self.llm = PeftModel.from_pretrained(self.llm, vars.PEFT_MODEL)

        self.reranker = SentenceTransformerRerank(
            model=vars.RERANK_MODEL, top_n=self.params.qe_reranker_top_n
        )

        self.index_service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            llm=self.index_llm_model,
            callback_manager=self.callback_manager,
        )

        self.vector_store_info = VectorStoreInfo(
            content_info="Financial documents for companies",
            metadata_info=[
                MetadataInfo(
                    name="year",
                    type="str",
                    description="Year is the only filter.\nYear of the financial document as a string.\nOne of ['2018', '2019', '2020', '2021', '2022', '2023'].\nUse '2023' if asked for most recent or current information.",
                ),
            ],
        )
        _logger.info("QueryEngine initialized")

    def _create_instance(self, index):
        # pipeline
        llm_pipeline = pipeline(
            "text-generation",
            model=self.llm,
            tokenizer=self.tokenizer,
            use_cache=True,
            device_map="auto",
            top_k=self.params.qe_top_k,
            repetition_penalty=self.params.qe_repetition_penalty,
            max_new_tokens=self.params.qe_max_new_tokens,
            do_sample=True,
            temperature=self.params.qe_temperature,
            num_return_sequences=1,
            eos_token_id=self.tokenizer("###")["input_ids"],
            pad_token_id=self.tokenizer.eos_token_id,
        )

        # Custom LLM Class which will be used for response generation
        responder = Responder(
            model=llm_pipeline,
            model_name=vars.MODEL_ID,
            max_tokens=self.params.qe_max_new_tokens,
            context_window=self.context_length,
        )

        # Configure model and embedding model
        tool_service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            llm=responder,
            callback_manager=self.callback_manager,
        )

        # Response Generator: Generates response for the sub-question
        response_synthesizer = get_response_synthesizer(
            response_mode="simple_summarize",
            text_qa_template=self.prompt_template,
            service_context=tool_service_context,
        )

        vector_retriever = VectorIndexAutoRetriever(
            index,
            vector_store_info=self.vector_store_info,
            service_context=tool_service_context,
            similarity_top_k=self.params.qe_similarity_top_k,
        )

        vector_query_engine = RetrieverQueryEngine(
            retriever=vector_retriever,
            response_synthesizer=response_synthesizer,
            node_postprocessors=[self.reranker],
        )

        _logger.info("Query Engine pipeline initialized")
        return vector_query_engine

    def _generate_answer(self, subquestion, tool_name, index, params):
        self.params = Config().from_proto(params)
        query_engine = self._create_instance(index)
        answer = query_engine.query(subquestion)
        qa_pair = SubQuestionAnswerPair(
            sub_q=SubQuestion(sub_question=subquestion, tool_name=tool_name),
            answer=answer.response,
            sources=answer.source_nodes,
        )
        return qa_pair

    def generate(self, subquestion: str, tool_name, index, params):
        qa_pair = self._generate_answer(subquestion, tool_name, index, params)
        citations = [
            {
                "filename": source_node.node.metadata["file_name"],
                "page": source_node.node.metadata["page_label"],
                "document_id": source_node.node.metadata.get("document_id", ""),
                "text": source_node.text,
                "node": source_node,
            }
            for source_node in qa_pair.sources
        ]
        return {
            "qa_pair": qa_pair,
            "citations": citations,
        }
