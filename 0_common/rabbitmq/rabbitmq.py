import pika

from . import variables as vars


class RabbitMQ:
    def __init__(self, queue_name):
        self.queue_name = queue_name
        credentials = pika.PlainCredentials(vars.RABBITMQ_USERNAME, vars.RABBITMQ_PASSWORD)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(vars.RABBITMQ_HOST, vars.RABBITMQ_PORT, "/", credentials)
        )
        self.channel = self.connection.channel()

        try:
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            print(f"Existence of queue: {self.queue_name} confirmed")

        except Exception as e:
            # Only raises an error when the parameters don't match the existing queue
            print(f"Error declaring queue {self.queue_name}: {e}")

    def send(self, message):
        # Default Exchange (Direct Exchange with Empty String Name)
        # When you specify an empty string as the exchange name when publishing a message,
        # RabbitMQ uses the routing key to determine which queue(s) to route the message to.
        # The routing key must match the queue name for the message to be delivered.
        self.channel.basic_publish(exchange="", routing_key=self.queue_name, body=message)
        print(f"Message sent to queue {self.queue_name}: {type(message)}")

    def receive(self, callback):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback, auto_ack=True)
        print(f"Listening for messages on queue {self.queue_name}")
        self.channel.start_consuming()
