import asyncio
import json
import sys
import threading
import time
from queue import Empty, Queue

import variables as vars
from db.client.client import Prisma
from pika.spec import Basic, BasicProperties
from rabbitmq import PubSub

queue = Queue()
ingestion_inprogess = True


def listen_for_messages():
    # Assumed Data Format:
    # {
    #     "id": "Attachment ID",
    #     "status": "Status of Indexing"
    # }
    def get_message(channel, method: Basic.Deliver, properties: BasicProperties, body):
        print(f"Message Properties: {method.delivery_tag} | {method.redelivered} | {method.routing_key}")

        parsed_message = json.loads(body.decode("utf-8"))
        attachment_id = parsed_message["id"]
        status = parsed_message["status"]

        queue.put((attachment_id, status))

    try:
        pubsub = PubSub(vars.ATTACHMENT_STATUS_EXCHANGE)
        pubsub.subscribe(callback=get_message)
    except Exception:
        global ingestion_inprogess
        ingestion_inprogess = False

        sys.exit(1)
    finally:
        pubsub.channel.stop_consuming()


async def worker_task():
    async def update_status(message, prisma):
        attachment_id, status = message
        await prisma.attachment.update(where={"id": attachment_id}, data={"status": status})
        print(f"Updated attachment status: {attachment_id} | {status}")

    try:
        prisma = Prisma()
        await prisma.connect()
        print("Connected...")
        while ingestion_inprogess or not queue.empty():
            try:
                attachment = queue.get(block=False)
                await update_status(attachment, prisma)
            except Empty:
                time.sleep(2)

        sys.exit(1)
    finally:
        await prisma.disconnect()


if __name__ == "__main__":
    thread = threading.Thread(target=listen_for_messages)
    thread.start()

    asyncio.run(worker_task())
