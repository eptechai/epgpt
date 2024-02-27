import asyncio
import logging
import os
import sys
import uuid

import openai
import variables as vars
from db.client.client import Prisma
from llama_index import (
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import OpenAI
from llama_index.node_parser import SimpleNodeParser
from storage import Storage

openai.api_key = vars.OPENAI_KEY
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES_FOLDER = os.path.join(BASE_DIR, "files")
VECTOR_STORAGE = os.path.join(BASE_DIR, "storage-v256")

os.makedirs(FILES_FOLDER, exist_ok=True)
os.makedirs(VECTOR_STORAGE, exist_ok=True)

prisma = Prisma()


def setup():
    # set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # loads hf embedding model
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en")

    # set service context so llama index knows what models to use
    node_parser = SimpleNodeParser.from_defaults(chunk_size=256, chunk_overlap=20)
    llm = OpenAI(model="gpt-3.5-turbo", temperature=0.4)

    service_context = ServiceContext.from_defaults(
        embed_model=embed_model, llm=llm, node_parser=node_parser
    )
    return service_context


def metadata(filename, files_ids, company):
    filename = filename.split("/")[-1]
    return {
        "ticker": filename.split("_")[0].split("/")[-1],
        "company_name": company,
        "document_type": filename.split("_")[2],
        "year": filename.split("_")[3].split(".")[0][-4:],
        "document_id": files_ids[company][filename],
    }


async def is_documents_table_empty():
    result = await prisma.document.find_first()
    return result is None


async def create_documents_build_index(
    corpus_files_bucket_name, corpus_indices_bucket_name, service_context
):
    if not await is_documents_table_empty():
        try:
            await prisma.document.delete_many(where={"source": "CORPUS"})
        except Exception as e:
            print(f"Something happened deleting db records: {e}")
    else:
        print("Skipping deletion step because documents table is empty!")

    gcs_corpus_files_client = Storage(corpus_files_bucket_name)
    gcs_corpus_indices_client = Storage(corpus_indices_bucket_name)

    files = gcs_corpus_files_client.list_files()
    downloaded_companies = []
    files_ids = {}
    for file in files:
        company, file_name = file.split("/")
        if company not in set(downloaded_companies):
            files_ids[company] = {}
            downloaded_companies.append(company)
            print(f"Creating directory: {company}")
            os.mkdir(f"{FILES_FOLDER}/{company}")
        gcs_corpus_files_client.download_file(file, f"{FILES_FOLDER}/{file}")

        document_id = uuid.uuid4()
        files_ids[company][file_name] = str(document_id)
        await prisma.document.create(
            data={
                "id": str(document_id),
                "name": file_name,
                "source": "CORPUS",
                "link": f"gs://{corpus_files_bucket_name}/{file}",
                "credentials": "CLOUD_STORAGE_CREDENTIALS",  # This is the env var that contains credentials
            }
        )
        print(f"Created file in documents table: {file_name}")

    companies = os.listdir(FILES_FOLDER)
    print(f"Downloaded folders: {companies}")
    for company in companies:
        vector_path = os.path.join(VECTOR_STORAGE, company)
        docs_path = os.path.join(FILES_FOLDER, company)

        print("Creating index...")
        docs = SimpleDirectoryReader(
            docs_path,
            file_metadata=lambda filename: metadata(filename, files_ids, company),
        ).load_data()

        index = VectorStoreIndex.from_documents(
            docs,
            service_context=service_context,
        )
        index.set_index_id(f"{company}_index")
        index.storage_context.persist(persist_dir=vector_path)
        gcs_corpus_indices_client.upload_folder(vector_path, company)


async def main():
    await prisma.connect()
    corpus_files_bucket_name = vars.CORPUS_FILE_BUCKET
    corpus_indices_bucket_name = vars.CORPUS_INDICES_BUCKET
    service_context = setup()
    await create_documents_build_index(
        corpus_files_bucket_name, corpus_indices_bucket_name, service_context
    )
    await prisma.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
