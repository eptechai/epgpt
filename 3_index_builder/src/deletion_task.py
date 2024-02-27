import json

import variables as vars
from attachment_proto.attachment_pb2 import AttachmentDeletionMessage
from logger import create_logger
from pika.spec import Basic, BasicProperties
from rabbitmq import PubSub, RabbitMQ
from storage import Storage

_logger = create_logger("conversation_index: deletion_task")


# Assumed Data Format:
# {
#     "id": "Conversation ID",
#     "filename": "Filename of file"
# }
def delete_index(channel, method: Basic.Deliver, properties: BasicProperties, body):
    _logger.debug(
        f"Message Properties: {method.delivery_tag} | {method.redelivered} | {method.routing_key}"
    )

    # Convert the binary stream to a text stream
    # Load into the AttachmentDeletionMessage object
    attachment = AttachmentDeletionMessage()
    attachment.ParseFromString(body)

    # Read the chat ID, file name and file stream from the dictionary
    conversation_id = attachment.conversationId
    attachment_id = attachment.id
    filename = attachment.fileName.rsplit(".", 1)[0]

    # Delete an index for the file
    try:
        # Upload the index to GCS
        storage = Storage(vars.CONV_INDICES_BUCKET_NAME)
        storage.delete_folder(remote_path=f"{conversation_id}/{filename}")

        status = "DELETED"
        _logger.info(
            f"Successfully deleted file: {filename} ({attachment_id}) | {conversation_id}"
        )
    except Exception:
        status = "ERRORED"
        _logger.exception(
            f"Unable to delete file: {filename} ({attachment_id}) | {conversation_id}"
        )
    finally:
        # Send the DELETION status message to the pubsub topic
        pubsub = PubSub(vars.ATTACHMENT_STATUS_EXCHANGE)
        pubsub.publish(
            json.dumps({"id": attachment_id, "filename": filename, "status": status})
        )
        _logger.info(f"Message sent to pubsub: {filename} | {status}")


def delete_indices():
    rabbitmq = RabbitMQ(vars.INDEX_DELETION_QUEUE)
    rabbitmq.receive(callback=delete_index)


if __name__ == "__main__":
    delete_indices()
