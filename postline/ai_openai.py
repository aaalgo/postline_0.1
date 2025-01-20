import json
from openai import OpenAI
from postline import Agent, Message, parse_message
from journal import play_journal


FIELDS_TO_COPY = ['From', 'To', 'Subject', 'Content-Type']

PRIMER_PROMPT_TMPL = """From: system@localdomain
To: {agent.address}
Subject: initialization
Content-Type: text/plain

You are an AI agent that communicates with the outside world through email messages.  Your email address is {agent.address}.  The incoming messages might be from human users, other AI agents, or the system itself.  You should respond to the messages as appropriate.  Make sure you generate the emails headers correctly.  If you decide to add a Subject, make it concise; or you could just leave it blank.
"""

PRIMER_RESPONSE_TMPL = """From: {agent.address}
To: system@localdomain
Subject: RE: initialization
Content-Type: text/plain

Yes, I'm ready to process messages.
"""

class GptAgent (Agent):

    def __init__ (self, address, storage=None):
        super().__init__(address, storage)

    def format_gpt_message (self, message: Message, serial_number):
        out = {}
        if message['From'] == self.address:
            out['role'] = 'assistant'
        else:
            out['role'] = 'user'
        message["X-Serial"] = str(serial_number)
        out['content'] = message.as_string() 
        del message['X-Serial']
        return out

    def format_context (self):
        journal = play_journal(self.address, self.journal)
        output = []
        output.append({'role': 'user', 'content': PRIMER_PROMPT_TMPL.format(agent=self)})
        output.append({'role': 'assistant', 'content': PRIMER_RESPONSE_TMPL.format(agent=self)})
        for idx, entry in enumerate(journal):
            output.append(self.format_gpt_message(entry.message, serial_number=idx))
        return output
    
    def stock_response (self):
        message = Message()
        message['From'] = self.address
        message['To'] = self.journal[-1].message['From']
        prev_subject = self.journal[-1].message['Subject']
        if prev_subject:
            message['Subject'] = 'RE: ' + prev_subject
        else:
            message['Subject'] = 'RE:'
        message['Content-Type'] = 'text/plain'
        message.set_content('This is the stock response.')
        return message

    def process (self, message: Message, app):
        self.append(message)
        messages = self.format_context()
        for message in messages:
            print('-'* 20, message['role'])
            print(message['content'])
        if not self.address.startswith('ai_'):
            resp = self.stock_response()
        else:
            client = OpenAI()
            response = client.chat.completions.create(
                model = 'gpt-4o',
                messages = messages,
                stream = False
            )
            # Get usage statistics from the response
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            print(f"Prompt tokens: {prompt_tokens}")
            print(f"Completion tokens: {completion_tokens}") 
            print(f"Total tokens: {total_tokens}")
            resp = parse_message(response.choices[0].message.content)
            resp['X-Total-Tokens'] = str(total_tokens)
        self.append(resp)
        print('-' * 20, 'generation')
        print(resp.as_string())
        app.send(resp)
