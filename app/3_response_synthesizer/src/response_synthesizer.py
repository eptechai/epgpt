import variables as vars
from llama_index import ServiceContext, get_response_synthesizer
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.prompts.base import PromptTemplate
from llama_index.prompts.prompt_type import PromptType
from llama_index.schema import NodeWithScore, QueryBundle, TextNode
from llm_utils import Config, Summarizer
from logger import create_logger
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer,
    pipeline,
)

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
        self.tokenizer = AutoTokenizer.from_pretrained(vars.MODEL_ID)

        self.llm = AutoModelForCausalLM.from_pretrained(
            vars.MODEL_ID,
            trust_remote_code=True,
            quantization_config=vars.BNB_CONFIG,
            device_map="auto",
        )

        _logger.info("Response Synthesizer initilized")

    def _create_nodes(self, qa_pairs):
        nodes = []
        for question, answer in qa_pairs.items():
            node_text = f"Sub question: {question}\nResponse: {answer}"
            nodes.append(NodeWithScore(node=TextNode(text=node_text)))
        return nodes

    # update parameters
    def _create_instance(self):
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, timeout=5)

        llm_pipeline = pipeline(
            "text-generation",
            model=self.llm,
            tokenizer=self.tokenizer,
            streamer=streamer,
            use_cache=True,
            device_map="auto",
            top_k=self.params.rs_top_k,
            repetition_penalty=self.params.rs_repetition_penalty,
            max_new_tokens=self.params.rs_max_new_tokens,
            do_sample=True,
            temperature=self.params.rs_temperature,
            num_return_sequences=1,
        )

        custom_llm = Summarizer(
            model=llm_pipeline,
            max_tokens=self.params.rs_max_new_tokens,
            context_window=self.context_length,
            model_name=vars.MODEL_ID,
        )

        service_context = ServiceContext.from_defaults(
            embed_model=self.embed_model,
            llm=custom_llm,
            callback_manager=self.callback_manager,
        )
        _logger.info(f"Service Context: {vars.EMBEDDING_MODEL} | {vars.MODEL_ID}")
        self.summarizer = get_response_synthesizer(
            response_mode="simple_summarize",
            text_qa_template=self.prompt_template,
            service_context=service_context,
            streaming=True,
        )
        _logger.info(f"Synthesizer setup: {self.params}")
        return streamer

    def initialize_synthesizer(self, query, qa_pairs, sources, params):
        self.query_str = query
        self.query = QueryBundle(query_str=query)
        self.nodes = self._create_nodes(qa_pairs=qa_pairs)
        self.additional_source_nodes = sources
        self.params = Config().from_proto(params)
        _logger.info(f"Request: {query} | {params}")

        return self._create_instance()

    def synthesize(self):
        _logger.info(f"Synthesizing answer: {self.query_str}")
        response = self.summarizer.synthesize(
            query=self.query,
            nodes=self.nodes,
            additional_source_nodes=self.additional_source_nodes,
        )
        return response
