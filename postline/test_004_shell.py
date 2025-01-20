#!/usr/bin/env python3
import sys
import json
import argparse
import subprocess as sp
from postline import App, Message, Entity

PROMPT = """
You are the middleman AI, which sits between the user and the bash command line of a recent Ubuntu system.  Both the user and the shell are represented by email addresses.  You'll receive user input from the user email address, and you'll send the commands to the email address shell@localdomain, in a JSON format (detailed below).  Are you get response from the shell, you'll interpret the outcome and send a message back to the user.

The address shell@localdomain only processes messages of Content-Type application/json with the following schema:

{
  "prompt": "The prompt to display to the user",
  "command": "echo Hello, world!",
  "confirm": false
}

- prompt: the prompt to display to the user before the command is run
- command: the command to run on the system
- confirm: whether to ask the user to confirm whether to run the command.  Please confirm for commands that might potentially damage the system.
"""

def make_reply_message (self_address, message, content):
    re = Message()
    re['From'] = self_address
    re['To'] = message['From']
    re['Content-Type'] = 'text/plain'
    re.set_content(content)
    return re

def make_message (self_address, to_address, content):
    message = Message()
    message['From'] = self_address
    message['To'] = to_address
    message['Content-Type'] = 'text/plain'
    message.set_content(content)
    return message

def run_command(command):
    """
    Executes a shell command, returning (stdout, stderr, returncode).
    """
    result = sp.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

class Shell (Entity):
    def __init__ (self, address):
        super().__init__(address)

    def init (self, app):
        pass

    def process (self, message, app):

        if message['Content-Type'] != 'application/json':
            raise ValueError('Message content type must be application/json')
        content = json.loads(message.get_content())
        prompt = content.get('prompt', '')
        command = content.get('command', '')
        confirm = content.get('confirm', False)
        print(prompt)
        if confirm:
            user_confirmation = input(f"Run this command? {command} (yes/no): ")
            if user_confirmation.lower() != "yes":
                app.send(make_reply_message(self.address, message, 'The user has declined to run the command'))
                return
        
        stdout, stderr, returncode = run_command(command)
        msg = make_reply_message(self.address, message,
                f'The return code of the command is {returncode}\n. See attachment for STDOUT and STDERR.  Use please this to generate a response to the user.'
                )
        msg.add_attachment(stdout, filename='stdout.txt')
        msg.add_attachment(stderr, filename='stderr.txt')
        app.send(msg)

class MyEntity (Entity):

    def __init__(self, address, to_address, reset=False):
        super().__init__(address)
        self.to_address = to_address
        self.reset = reset

    def init (self, app):
        if self.reset:
            app.send(make_message(self.address, self.to_address, PROMPT))
        else:
            user_input = input("??? ")
            app.send(make_message(self.address, self.to_address, user_input))

    def process (self, message, app):
        if not message is None:
            self.append(message)
            print("-" * 80)
            print(message.as_string())
        user_input = input("??? ")
        app.send(make_reply_message(self.address, message, user_input))

def main():
    parser = argparse.ArgumentParser(description='Send a message')
    parser.add_argument('--to', help='Recipient address')
    parser.add_argument('--init', action='store_true', help='Initialize the conversation')
    args = parser.parse_args()
    app = App()
    app.add_entity(Shell('shell@localdomain'))
    app.add_entity(MyEntity('user1@localdomain', args.to, args.init))
    app.run()

if __name__ == "__main__":
    main()
