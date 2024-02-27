from typing import Any

from llama_index.indices.base import BaseIndex
from llama_index.question_gen.types import SubQuestion
from llama_index.schema import NodeWithScore
from query_engine import QueryEngine, SubQuestionAnswerPair


class QueryEngineMock(QueryEngine):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return super().__call__(*args, **kwds)

    def generate(self, subquestion: str, tool_name, index: BaseIndex, params):
        node_id = [
            values["node_ids"]
            for key, values in index.docstore.to_dict()["docstore/ref_doc_info"].items()
        ][0][0]

        citation = index.docstore.get_node(node_id=node_id)
        source_node = NodeWithScore(node=citation, score=1)
        return {
            "qa_pair": SubQuestionAnswerPair(
                sub_q=SubQuestion(sub_question=subquestion, tool_name=tool_name),
                answer="Mocked Response",
                sources=[source_node],
            ),
            "citations": [
                {
                    "filename": source_node.node.metadata["file_name"],
                    "page": source_node.node.metadata["page_label"],
                    "document_id": source_node.node.metadata.get("document_id", ""),
                    "text": source_node.text,
                    "node": source_node,
                }
            ],
        }
