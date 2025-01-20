#!/usr/bin/env python3
import sys
import json
import pika
import argparse
from postline import App, Message, Entity
import config

class MyEntity (Entity):

    def __init__(self, address, to_address):
        super().__init__(address)
        message = Message()
        message['From'] = self.address
        message['To'] = to_address
        message['Content-Type'] = 'text/plain'
        self.message = message

    def init (self, app):
        self.process(None, app)

    def process (self, message, app):
        if not message is None:
            self.append(message)
            print("-" * 80)
            print(message.as_string())
        user_input = input(">>> ")
        self.message.set_content(user_input)
        app.send(self.message)

def main():
    parser = argparse.ArgumentParser(description='Send a message')
    parser.add_argument('--to', help='Recipient address')
    parser.add_argument('--from', default='user1@localdomain', help='Sender address') 
    args = parser.parse_args()
    From = getattr(args, 'from')
    app = App()
    app.add_entity(MyEntity(From, args.to))
    app.run()

if __name__ == "__main__":
    main()
