import csv
from pathlib import Path
import warnings
from langchain._api import LangChainDeprecationWarning
warnings.simplefilter("ignore", category=LangChainDeprecationWarning)


from llama_index import VectorStoreIndex, StorageContext

from framework.vector_store import VectorRetriever
from vector_stores.node_parser import basic_parse_nodes
from storage import Storage


class BasicVectorStore(VectorRetriever):

    def __init__(self, store_type="pg_vector", node_parser_callable=basic_parse_nodes):
        super().__init__(store_type)
        self.node_parser = node_parser_callable
        # note: only used with the AutoRetriever, which is currently disabled

    def load_vector_retriever(self):
        if not self.index:
            # todo currently we just create and index if there is no table; we will want to recreate if count of rows
            #  are different than number of principles in our data
            nodes = self.node_parser()
            print(len(nodes))
            if not self.vector_store.check_embeddings(len(nodes)):
                storage_context = StorageContext.from_defaults(vector_store=self.vector_store.vector_store)
                self.index = VectorStoreIndex(nodes, storage_context=storage_context)
            else:
                self.index_from_vector_store()
            self.set_vector_retriever()


_store = BasicVectorStore()


def initialize():
    _store.load_vector_retriever()


def get_vector_store():
    _store.load_vector_retriever()
    return _store

if __name__ == '__main__':
    initialize()