from logger import create_logger
from transformers import TextIteratorStreamer, pipeline

from model import GPT, Config

_logger = create_logger("model:message")


class Message:
    def __init__(self, id, prompt, config: Config, chatbot: GPT):
        self.id = id
        self.prompt = prompt
        self.config = config
        self.chatbot = chatbot

        self.streamer = TextIteratorStreamer(chatbot.tokenizer, skip_prompt=True, timeout=5)

        _logger.info(f"GPTDialogue initialized!: {prompt} | {config}")

    def create_instance(self):
        """
        Creates the Streaming HuggingFacePipeline instance
        """
        llm_pipeline = pipeline(
            "text-generation",
            model=self.chatbot.model,
            tokenizer=self.chatbot.tokenizer,
            streamer=self.streamer,
            top_k=self.config.top_k,
            temperature=self.config.temperature,
            max_new_tokens=self.config.max_new_tokens,
            repetition_penalty=self.config.repetition_penalty,
            # Non-configurable parameters
            use_cache=True,
            do_sample=True,
            device_map="auto",
            num_return_sequences=1,
            eos_token_id=self.chatbot.tokenizer("###")["input_ids"],
            pad_token_id=self.chatbot.tokenizer.eos_token_id,
        )

        return llm_pipeline

    def converse(self):
        """
        Initiates a dialogue with the chatbot
        :return:
        """
        chatbot = self.create_instance()
        response = chatbot(self.prompt)
        print(f"Response: {response}")

        # Reference Response Structure
        # @dataclass
        # class GPTResponse:

        #     @dataclass
        #     class Chunk:
        #         file_name: str
        #         page_number: int
        #         content: str

        #     response: str
        #     references: List[Chunk]

        return {
            "id": self.id,
            "response": response[0].get("generated_text"),
        }
