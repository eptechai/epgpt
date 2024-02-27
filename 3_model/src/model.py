from dataclasses import dataclass

import torch
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from logger import create_logger
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from variables import LOCAL_QLORA_ADAPTER_FOLDER, USE_7B

_logger = create_logger("model:model")


class GPT:
    # Model config
    context_length: int = 2048
    llm_model_path: str = "tiiuae/falcon-40b" if not USE_7B else "tiiuae/falcon-7b"
    embedding_model_path: str = "BAAI/bge-base-en"

    def __init__(self) -> None:
        """
        Initializes the chatbot with specified parameters
        """
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=50, length_function=len
        )
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.embedding_model_path,
            model_kwargs={"device": "cuda"},
            encode_kwargs={"normalize_embeddings": True},
        )

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        # Download the Falcon 40B LLM Model
        # Takes 30 mins to run
        # Note that `load_in_4bit` is only compatible with GPUs, hence it is not possible to run on a CPU.
        pretrained_model = AutoModelForCausalLM.from_pretrained(
            self.llm_model_path,
            trust_remote_code=True,
            quantization_config=bnb_config,
            device_map="auto",
        )

        self.model = PeftModel.from_pretrained(pretrained_model, LOCAL_QLORA_ADAPTER_FOLDER)
        _logger.info(f"Successfully loaded the model: {self.llm_model_path}")
        _logger.info("DocumentReaderGPT initialized!")


@dataclass
class Config:
    """
    Config object for the LLM model
    """

    # TODO: Read defaults from DB/env variables
    k: int = 5
    top_k: int = 5
    temperature: float = 0.25
    max_new_tokens: int = 250
    score_threshold: float = 0.7
    repetition_penalty: float = 1.2

    use_only_uploaded: bool = False

    @classmethod
    def from_dict(cls, config):
        k = int(config.get("k", cls.k))
        top_k = int(config.get("top_k", cls.top_k))
        temperature = float(config.get("temperature", cls.temperature))
        max_new_tokens = int(config.get("max_new_tokens", cls.max_new_tokens))
        score_threshold = float(config.get("score_threshold", cls.score_threshold))

        repetition_penalty = float(config.get("repetition_penalty", cls.repetition_penalty))
        use_only_uploaded = bool(config.get("use_only_uploaded", cls.use_only_uploaded))

        obj = cls(
            k,
            top_k,
            temperature,
            max_new_tokens,
            score_threshold,
            repetition_penalty,
            use_only_uploaded,
        )
        return obj

    @classmethod
    def from_proto(cls, config):
        extracted_config = {
            "k": config.get("k"),
            "top_k": config.get("topK"),
            "temperature": config.get("temperature"),
            "max_new_tokens": config.get("maxNewTokens"),
            "score_threshold": config.get("scoreThreshold"),
            "repetition_penalty": config.get("repetitionPenalty"),
        }

        return cls.from_dict(extracted_config)

    def to_dict(self):
        record = self.__dict__
        record.pop("use_only_uploaded")
        return record

    def __post_init__(self) -> None:
        if not (1 <= self.k <= 15):
            raise ValueError("k should belong to [1, 15]")

        if not (1 <= self.top_k <= 25):
            raise ValueError("top_k should belong to [1, 25]")

        if not (0 <= self.temperature <= 3):
            raise ValueError("temperature should belong to [0, 3]")

        if not (1 <= self.max_new_tokens <= 500):
            raise ValueError("max_new_tokens should belong to [1, 500]")

        if not (0 <= self.score_threshold <= 5):
            raise ValueError("score_threshold should belong to [0, 5]")
