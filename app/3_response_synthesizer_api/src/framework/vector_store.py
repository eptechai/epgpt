import psycopg2
from psycopg2.errors import UndefinedTable
from llama_index import ServiceContext, VectorStoreIndex, StorageContext
from llama_index.indices.vector_store.retrievers.retriever import VectorIndexRetriever
from llama_index.indices.vector_store.retrievers.auto_retriever import (
    VectorIndexAutoRetriever,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.postgres import PGVectorStore

from variables import (
    DBNAME,
    PG_CONNECTION_DICT,
    PG_URL,
    SIMILARITY_TOP_K,
    USE_AUTO_RETRIEVER,
)

class VectorStore:

    def __init__(self, store_type: str, embed_dim: int, embedding_table_name: str='test'):
        self.store_type = store_type
        self.embed_dim = embed_dim
        self.embedding_table_name = embedding_table_name
        self.set_vector_store()

    def set_vector_store(self):
        match self.store_type:
            case "pg_vector":
                self.vector_store = PGVectorStore.from_params(
                    database=DBNAME,
                    host=PG_URL.host,
                    password=PG_URL.password,
                    port=PG_URL.port,
                    user=PG_URL.username,
                    table_name=self.embedding_table_name,
                    embed_dim=self.embed_dim,
                    hybrid_search=True,
                    text_search_config="english",
                )


    def check_embeddings(self, advice_count: int = 0):
        match self.store_type:
            case "pg_vector":
                value = False
                # get advice principles list
                try:
                    conn = psycopg2.connect(**PG_CONNECTION_DICT)
                    with conn.cursor() as cursor:
                        cursor.execute( f"SELECT count(*) FROM data_{self.embedding_table_name}")
                        table_count = cursor.fetchone()[0]
                        print("Table Counts:", table_count)
                        if table_count == advice_count:
                            value = True
                        else:
                            cursor.execute( f"DROP TABLE data_{self.embedding_table_name}")
                            conn.commit()
                    return value
                except Exception as e:
                    message = ("CloudSQL auth proxy required for to use RAG locally. If installed, run "
                               "'./cloud-sql-proxy sitch-core:us-west2:core-beta' from the terminal. If not installed"
                               " yet, see: https://cloud.google.com/sql/docs/postgres/connect-instance-auth-proxy")
                    if type(e) == UndefinedTable:
                        return value
                    raise type(e)(message)


class VectorRetriever:

    def __init__(self, store_type: str, embedding_table_name: str = "test"):
        self.service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-4"))
        self.vector_store = VectorStore(store_type=store_type, embed_dim=1536, embedding_table_name=embedding_table_name)
        self.vector_store_info = None
        self.vector_retriever = None
        self.index = None
        self.use_auto_retriever = USE_AUTO_RETRIEVER

    def index_from_vector_store(self):
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store.vector_store,
                                                        service_context=self.service_context)

    def set_query_engine(self):
        self.query_engine = self.index.as_query_engine()

    def set_vector_retriever(self):
        if self.use_auto_retriever:
            self.vector_retriever = VectorIndexAutoRetriever(
                index=self.index,
                vector_store_info=self.vector_store_info,
                service_context=self.service_context,
                similarity_top_k=SIMILARITY_TOP_K,
                verbose=True,
            )
        else:
            self.vector_retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=4,
                verbose=True,
                filters=[],
            )
