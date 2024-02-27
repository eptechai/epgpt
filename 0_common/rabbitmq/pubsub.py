import pika

from . import variables as vars


class PubSub:
    def __init__(self, exchange_name):
        self.exchange_name = exchange_name
        credentials = pika.PlainCredentials(vars.RABBITMQ_USERNAME, vars.RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(vars.RABBITMQ_HOST, vars.RABBITMQ_PORT, "/", credentials)
        )
        self.channel = self.connection.channel()

        try:
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type="fanout")
            print(f"Existence of exchange: {self.exchange_name} confirmed")

        except Exception as e:
            # Only raises an error when the parameters don't match the existing queue
            print(f"Error declaring exchange {self.exchange_name}: {e}")

    def publish(self, message: str):
        self.channel.basic_publish(exchange=self.exchange_name, routing_key="", body=message)
        print(f"Message sent to exchange {self.exchange_name}: {message}")

    def subscribe(self, callback):
        result = self.channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(f"Listening for messages on exchange: {self.exchange_name} | queue {queue_name}")
        self.channel.start_consuming()

    def create_exclusive_queue(self):
        result = self.channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name)
        return queue_name
