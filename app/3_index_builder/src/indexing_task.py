import json
import os

import variables as vars
from attachment_proto.attachment_pb2 import Attachment
from llama_index import ServiceContext, SimpleDirectoryReader, VectorStoreIndex
from llama_index.callbacks import (
    CallbackManager,
    LlamaDebugHandler,
    OpenInferenceCallbackHandler,
)
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import OpenAI
from logger import create_logger
from pika.spec import Basic, BasicProperties
from rabbitmq import PubSub, RabbitMQ
from storage import Storage

_logger = create_logger("index_builder: indexing_task")

# Assumption #1: Embedding model and TextSplitter objects are the same for all indices
# Assumption #2: It is more efficient to load the embedding model once, instead of loading it each time


# Assumed Data Format:
# {
#     "id": "Conversation ID",
#     "filename": "Filename of file",
#     "file": "Binary stream of file"
# }


def _init_service_context():
    # callback manager

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_handler = OpenInferenceCallbackHandler()
    callback_manager = CallbackManager([llama_debug, callback_handler])
    # service context

    embed_model = HuggingFaceEmbedding(model_name=vars.EMBED_MODEL_NAME)
    llm_model = OpenAI(model=vars.LLM_MODEL_NAME, temperature=0)

    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=llm_model,
        callback_manager=callback_manager,
    )
    return service_context


tool_service_context = _init_service_context()


def create_index(channel, method: Basic.Deliver, properties: BasicProperties, body):
    _logger.debug(
        f"Message Properties: {method.delivery_tag} | {method.redelivered} | {method.routing_key}"
    )

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
        # Upload the index to GCS
        storage = Storage(vars.CONV_INDICES_BUCKET_NAME)

        metadata = lambda filename: {  # noqa: E731
            "conversation_id": conversation_id,
            "document_id": attachment_id,
        }
        doc = SimpleDirectoryReader(
            input_files=[file_path], file_metadata=metadata
        ).load_data()

        index = VectorStoreIndex.from_documents(
            doc, service_context=tool_service_context
        )

        index.set_index_id(f"{conversation_id}_index")
        # rebuild storage context
        index.storage_context.persist(persist_dir=folder_path)
        storage_path = f"{conversation_id}/{filename}"
        storage.upload_folder(folder_path, storage_path)
        _logger.info(f"File stored in: {storage_path}")

        status = "INDEXED"
        _logger.info(
            f"Successfully indexed file: {filename} ({attachment_id}) | {conversation_id}"
        )
    except Exception as exc:
        status = "ERRORED"

        _logger.exception(
            f"Unable to index file: {filename} ({attachment_id}) | {conversation_id} | {exc}"
        )
    finally:
        # TODO: Check if the channel needs to be closed

        # Send the INDEXED status message to the pubsub topic
        pubsub = PubSub(vars.ATTACHMENT_STATUS_EXCHANGE)
        pubsub.publish(
            json.dumps({"id": attachment_id, "filename": filename, "status": status})
        )
        _logger.info(f"Message sent to pubsub: {filename} | {status}")


def index_builder():
    rabbitmq = RabbitMQ(vars.NEW_ATTACHMENT_QUEUE)
    rabbitmq.receive(callback=create_index)


if __name__ == "__main__":
    index_builder()
