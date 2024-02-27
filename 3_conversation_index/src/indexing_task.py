import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

import variables as vars
from attachment_proto.attachment_pb2 import Attachment
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from logger import create_logger
from pika.spec import Basic, BasicProperties
from rabbitmq import PubSub, RabbitMQ
from storage import Storage

_logger = create_logger("conversation_index: indexing_task")

# Assumption #1: Embedding model and TextSplitter objects are the same for all indices
# Assumption #2: It is more efficient to load the embedding model once, instead of loading it each time
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50, length_function=len)
embedding_model = HuggingFaceEmbeddings(
    model_name=os.path.join(os.path.dirname(__file__), "../gen_deps/embedding-model"),
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


# Assumed Data Format:
# {
#     "id": "Conversation ID",
#     "filename": "Filename of file",
#     "file": "Binary stream of file"
# }
def create_index(channel, method: Basic.Deliver, properties: BasicProperties, body):
    _logger.debug(f"Message Properties: {method.delivery_tag} | {method.redelivered} | {method.routing_key}")

    # Convert the binary stream to a text stream
    # Use json.loads() to convert the text stream to a dictionary
    attachment = Attachment()
    attachment.ParseFromString(body)

    # Read the chat ID, file name and file stream from the dictionary
    conversation_id = attachment.conversationId
    attachment_id = attachment.id
    filename = attachment.fileName.rsplit(".", 1)[0]

    # Path where the file will be downloaded
    file_path = os.path.join(vars.TEMP_INDICES_DIR, filename)
    with open(file_path, "wb") as file_type:
        file_type.write(attachment.fileContents)

    folder_path = os.path.join(vars.CREATED_INDICES_DIR, attachment_id)

    # Create an index for the file
    # TODO: Check if PyPDFLoader can use a in-memory file stream
    try:
        documents = PyPDFLoader(file_path).load()
        chunks = text_splitter.split_documents(documents)
        index = FAISS.from_documents(chunks, embedding=embedding_model)
        index.save_local(folder_path, filename)

        # Upload the index to GCS
        storage = Storage(vars.CONV_INDICES_BUCKET_NAME)

        for file_type in ["faiss", "pkl"]:
            storage.upload_file(
                os.path.join(folder_path, f"{filename}.{file_type}"),
                f"{conversation_id}/{filename}.{file_type}",
            )
        status = "INDEXED"
        _logger.info(f"Successfully indexed file: {filename} ({attachment_id}) | {conversation_id}")
    except Exception as exc:
        status = "ERRORED"

        _logger.exception(f"Unable to index file: {filename} ({attachment_id}) | {conversation_id}")
    finally:
        # TODO: Check if the channel needs to be closed
        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Send the INDEXED status message to the pubsub topic
        pubsub = PubSub(vars.ATTACHMENT_STATUS_EXCHANGE)
        pubsub.publish(json.dumps({"id": attachment_id, "filename": filename, "status": status}))
        _logger.info(f"Message sent to pubsub: {filename} | {status}")


def index_builder():
    rabbitmq = RabbitMQ(vars.NEW_ATTACHMENT_QUEUE)
    rabbitmq.receive(callback=create_index)


if __name__ == "__main__":
    index_builder()
