import variables as vars
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index import VectorStoreIndex, SimpleDirectoryReader, get_response_synthesizer
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.prompts.base import PromptTemplate
from llama_index.prompts.prompt_type import PromptType
from llama_index.schema import NodeWithScore, QueryBundle, TextNode
from llm_utils import Config
from llama_index.llms.openai import OpenAI
from vector_stores.basic_vector_store import get_vector_store

from logger import create_logger

_logger = create_logger("response_synthesizer:model")


class ResponseSynthesizer(object):
    prompt_template = PromptTemplate(
        vars.TEXT_FINAL_PROMPT_TMPL, prompt_type=PromptType.QUESTION_ANSWER
    )

    def __init__(self) -> None:
        self.context_length = vars.CONTEXT_WINDOW
        llama_debug = LlamaDebugHandler(print_trace_on_end=True)
        callback_handler = OpenInferenceCallbackHandler()
        self.callback_manager = CallbackManager([llama_debug, callback_handler])
        self.embed_model = HuggingFaceEmbedding(model_name=vars.EMBEDDING_MODEL)
        self.vector_store = get_vector_store()
        self.llm = OpenAI(model="gpt-4")
        _logger.info("Response Synthesizer initilized")

    def _create_nodes(self, qa_pairs):
        nodes = []
        for question, answer in qa_pairs.items():
            node_text = f"Sub question: {question}\nResponse: {answer}"
            nodes.append(NodeWithScore(node=TextNode(text=node_text)))
        return nodes

    # update parameters
    def _create_instance(self):

        self.summarizer = get_response_synthesizer(
            response_mode="simple_summarize",
            text_qa_template=self.prompt_template,
            service_context=self.vector_store.service_context
        )

        self._query_engine = RetrieverQueryEngine(
            retriever=self.vector_store.vector_retriever,
            response_synthesizer=self.summarizer)
        
        response = self.synthesize()
       
        return response
    

    def initialize_synthesizer(self, query, qa_pairs, use_rag=False):
        self.query_str = query
        self.query = QueryBundle(query_str=query)
        self.use_rag = use_rag
        _logger.info(f"Request: {query} ")

        return self._create_instance()


    def synthesize(self):
        _logger.info(f"Synthesizing answer: {self.query_str}")
        if self.use_rag:
            result = self._query_engine.query(
                self.query_str
            )
            response = result.response
            print(result.source_nodes)
        else:
            response = self.llm.complete(self.query_str).text
        return response
