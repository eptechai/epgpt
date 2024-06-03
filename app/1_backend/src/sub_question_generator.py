import uuid
from typing import Dict

from llama_index import QueryBundle
from llama_index.llms import OpenAI
from llama_index.question_gen.openai_generator import OpenAIQuestionGenerator
from llama_index.tools import ToolMetadata
from variables import OPENAI_KEY, SUB_QUESTION_MODEL_NAME


class SubQuestionGenerator(object):
    def __init__(self, companies: Dict = {}) -> None:
        with open("subquestion_prompt.txt") as file:
            prompt_template = file.read()

        self.tool_metadata = self.get_tool_metadata(companies=companies)

        args = {"api_key": OPENAI_KEY, "temperature": 0}
        if SUB_QUESTION_MODEL_NAME:
            args.update({"model": SUB_QUESTION_MODEL_NAME})

        llm = OpenAI(**args)
        self.question_gen = OpenAIQuestionGenerator.from_defaults(
            prompt_template_str=prompt_template,
            llm=llm,
        )

    def get_tool_metadata(self, companies: Dict):
        metadata = []
        for company, sub_sector in companies.items():
            tool = ToolMetadata(
                name=f"{company}",
                description=(
                    f"Provides information about the company {company}. "
                    f"This company belongs to the sub sector {sub_sector}. "
                    "A competitor is another company in the same sub_sector. "
                    "Use this sub_sector to find competitors if asked in the question."
                ),
            )
            metadata.append(tool)
        return metadata

    def generate_subquestions(self, query: str):
        # generate sub-questions
        sub_questions = self.question_gen.generate(
            tools=self.tool_metadata,
            query=QueryBundle(query),
        )
        sub_questions_list = [
            (subq.sub_question, subq.tool_name, str(uuid.uuid4())) for subq in sub_questions
        ]
        return sub_questions_list
