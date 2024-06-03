from pathlib import Path
from variables import CUR_DIR

from typing import Callable

from llama_index import SimpleDirectoryReader
from llama_index.schema import TextNode
from llama_index.node_parser import SimpleNodeParser


def basic_parse_nodes(filetypes=['.txt', '.pdf', '.docx', '.csv']):
    
    rag_path = Path(CUR_DIR, "temp", "Piston")
    node_parser = SimpleNodeParser.from_defaults(chunk_size=256, chunk_overlap=20)
    documents = SimpleDirectoryReader(rag_path, required_exts=filetypes, recursive=True).load_data()
    print(len(documents))
    
    nodes = node_parser.get_nodes_from_documents(documents)
    return nodes

def csv_parse_nodes(service_callable: Callable|None = None, main_field_name:str|None = None):
    if service_callable == None:
        return basic_parse_nodes(filetypes=['.csv'])
    if main_field_name is None:
        raise ValueError("No field name has been added to be indexed")
    return [TextNode(text=row[main_field_name]) for row in service_callable()]

