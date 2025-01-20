from abc import ABC, abstractmethod
from collections import defaultdict
import pickle
from email.parser import Parser
from email.policy import default as default_policy
from email.message import EmailMessage as Message
import pika
import config

# We use email.message.EmailMessage as the default Message type

def parse_message (message):
    if isinstance(message, bytes):
        message = message.decode('utf-8')
    elif isinstance(message, str):
        pass
    else:
        raise ValueError(f"Invalid message type: {type(message)}")
    return Parser(policy=default_policy).parsestr(message)

# Storage is a journal storage
# Conceptually it's a mapping from address to a list of journal entries
# Each journal entry has an Key, with the following requirements:
#   - It must be unique for the address
#   - For each address, the Key must be increasing by order
#   - It does not have to be consecutive, but it can be.
#   - Different addresses may or may not have the same Key.

class Entry:
    # journal entry
    def __init__(self, message: Message, key = None):
        self.message = message
        self.key = key  # database key

class Storage(ABC):
    # This is the journal storage
    def __init__(self):
        pass

    @abstractmethod
    def store(self, address, entry):
        # save the entry, return the key
        pass

    @abstractmethod
    def retrieve(self, address, since=None, max=None):
        pass

class MemoryStorage (Storage):
    def __init__(self):
        super().__init__()
        self.lookup = defaultdict(list)
    
    def load (self, path):
        with open(path, 'rb') as f:
            self.lookup = pickle.load(f)

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.lookup, f)

    def store(self, address, entry):
        journal = self.lookup[address]
        entry.key = len(journal)
        journal.append(entry)

    def retrieve(self, address, since=None, max=None):
        journal = self.lookup[address]
        if since is not None:
            journal = journal[since:]
        if max is not None:
            journal = journal[:max]
        return journal

class Entity:
    def __init__(self, address, storage = None):
        self.address = address
        self.storage = storage
        self.journal = []
        if self.storage:
            self.journal = self.storage.retrieve(self.address)

    def append (self, message: Message):
        entry = Entry(message)
        if self.storage:
            self.storage.store(self.address, entry)
        self.journal.append(entry)
    
    def process (self, message: Message, app):
        self.append(message)


class Agent (Entity):
    pass

class App:
    def __init__(self):
        self.storage = MemoryStorage()
        self.entities = {}
        self.connection = None
        self.channel = None

    def add_entity (self, entity):
        assert not entity.address in self.entities
        self.entities[entity.address] = entity

    def send (self, message):
        out_body = message.as_string()
        print('-' * 20)
        print("Sending message")
        print(out_body)
        print('-' * 20)
        to_addresses = [addr.strip() for addr in message['To'].split(',')]
        for to_address in to_addresses:
            routing_key = to_address.replace('@', '.')
            print(f"Sending message to {routing_key}")
            self.channel.basic_publish(exchange=config.RABBITMQ_EXCHANGE, routing_key=routing_key, body=out_body)

    def stop (self):
        self.channel.stop_consuming()

    def run (self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                credentials=pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
            )
        )
        channel = self.connection.channel()
        self.channel = channel
        channel.exchange_declare(exchange=config.RABBITMQ_EXCHANGE, exchange_type='topic')

        def processor (ch, method, properties, body):
            address = method.routing_key.replace('.', '@', 1)
            message = parse_message(body)
            entity = self.entities.get(address, None)
            if entity is None:
                print(f"No entity found for {address}")
                return
            entity.process(message, self)

        for entity in self.entities.values():
            queue_name = entity.address.replace('@', '.')
            channel.queue_declare(queue=queue_name)
            channel.queue_bind(queue=queue_name, exchange=config.RABBITMQ_EXCHANGE, routing_key=queue_name)
            channel.basic_consume(queue=queue_name, on_message_callback=processor, auto_ack=True)
        
        for entity in self.entities.values():
            entity.init(self)

        channel.start_consuming()
        self.connection.close()
