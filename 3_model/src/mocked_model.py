from model import GPT
from transformers import AutoTokenizer


class MockedGPT:
    context_length = 2048

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(GPT.llm_model_path)
