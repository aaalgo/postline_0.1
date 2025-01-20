#!/usr/bin/env python3
import pika
from postline import parse_message
from ai_openai import GptAgent
from sql_storage import SqlStorage, create_engine
import config

class Processor:
    def __init__ (self, storage):
        self.storage = storage
        self.ch = None

    def send (self, message):
        out_body = message.as_string()
        to_addresses = [addr.strip() for addr in message['To'].split(',')]
        for to_address in to_addresses:
            routing_key = to_address.replace('@', '.')
            print(f"Sending message to {routing_key}")
            self.ch.basic_publish(exchange=config.RABBITMQ_EXCHANGE, routing_key=routing_key, body=out_body)

    def __call__ (self, ch, method, properties, body):
        """Process a message from the queue"""
        print("Incoming message", method.routing_key)
        print(">"*20)
        print(body)
        self.ch = ch
        message = parse_message(body)
        address = method.routing_key.replace('.', '@', 1)
        agent = GptAgent(address, self.storage)
        agent.process(message, self)

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_HOST)
    )
    channel = connection.channel()
    
    domain = f"agents.{config.DOMAIN}"
    routing_key = f"*.{domain}"

    channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE, exchange_type='topic')
    channel.queue_declare(queue=domain)
    channel.queue_bind(queue=domain, exchange=config.RABBITMQ_EXCHANGE, routing_key=routing_key)

    engine = create_engine(config.DB_URL)
    storage = SqlStorage(engine)
    processor = Processor(storage)

    channel.basic_consume(
        queue=domain,
        on_message_callback=processor,
        auto_ack=True
    )
    print(f"Using exchange {config.RABBITMQ_EXCHANGE}")
    print(f"Waiting for messages on {routing_key}. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == '__main__':
    main()
