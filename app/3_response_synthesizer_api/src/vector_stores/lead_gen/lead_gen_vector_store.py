import csv
from pathlib import Path
from typing import Dict, Union
import warnings
from variables import CUR_DIR
from langchain._api import LangChainDeprecationWarning
warnings.simplefilter("ignore", category=LangChainDeprecationWarning)
import pandas as pd


from llama_index import VectorStoreIndex, StorageContext, ServiceContext
from llama_index.llms.openai import OpenAI


from framework.vector_store import VectorRetriever
from vector_stores.node_parser import csv_parse_nodes
from storage import Storage

from llama_index.extractors import SummaryExtractor

def get_proposals():
    rag_path = Path(CUR_DIR, "temp", "Piston", "valere_proposals.csv")
    data = pd.read_csv(rag_path)
    data = data.loc[~data["Job Description"].isna()]
    return data.to_dict("records")

def get_projects():
    rag_path = Path(CUR_DIR, "temp", "Piston", "valere_projects.csv")
    data = pd.read_csv(rag_path)
    data = data.loc[~data["Description"].isna()]
    return data.to_dict("records")



class LeadGenVectorStore:

    def __init__(self, store_type="pg_vector"):

        self.retrievers: Dict[str, Dict[str, Union[str, list, VectorRetriever, VectorStoreIndex]]] = {
            "proposals": {
                "retriever": VectorRetriever(store_type=store_type, embedding_table_name="proposals"),
                "field": "Job Description",
                "exclude": []
                }
                ,
            "projects": {
                "retriever": VectorRetriever(store_type=store_type, embedding_table_name="projects"),
                "field": "Description",
                "exclude": []
                }
        }
        self.indices = []
        # note: only used with the AutoRetriever, which is currently disabled


    def load_vector_retriever(self):
        
        # todo currently we just create and index if there is no table; we will want to recreate if count of rows
        #  are different than number of principles in our data
        for name, retriever  in self.retrievers.items():
            print(name)
            nodes = csv_parse_nodes(getattr(self, "get_" + name), retriever["field"])
            if not retriever["retriever"].vector_store.check_embeddings(len(nodes)):
                storage_context = StorageContext.from_defaults(vector_store=retriever["retriever"].vector_store.vector_store)
                retriever["retriever"].index = VectorStoreIndex(nodes, storage_context=storage_context)
            else:
                retriever["retriever"].index_from_vector_store()
            retriever["retriever"].set_vector_retriever()


    def get_proposals(self):
        rag_path = Path(CUR_DIR, "temp", "Piston", "valere_proposals.csv")
        data = pd.read_csv(rag_path)
        data = data.loc[~data["Job Description"].isna()]
        return data.to_dict("records")

    def get_projects(self):
        rag_path = Path(CUR_DIR, "temp", "Piston", "valere_projects.csv")
        data = pd.read_csv(rag_path)
        data = data.loc[~data["Description"].isna()]
        return data.to_dict("records")


_store = LeadGenVectorStore()


def initialize():
    _store.load_vector_retriever()


def get_vector_store():
    _store.load_vector_retriever()
    return _store

if __name__ == '__main__':
    initialize()