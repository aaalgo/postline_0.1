from email import policy
from email.parser import Parser
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import postline

Base = declarative_base()

AddressType = String(60)

class Message (Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(AddressType, nullable=False, index=True)   # belong to this address
    content = Column(Text, nullable=False)

class SqlStorage (postline.Storage):
    def __init__(self, engine):
        super().__init__()
        assert engine is not None
        self.engine = engine
    
    def store(self, address, entry):
        with Session(self.engine) as session:
            sqlMessage = Message(address=address, content=entry.message.as_string())
            session.add(sqlMessage)
            session.commit()
            entry.key = sqlMessage.id

    def retrieve(self, address, since=None, max=None):
        with Session(self.engine) as session:
            messages = session.query(Message).filter(Message.address == address)
            if since:
                messages = messages.filter(Message.id >= since)
            messages = messages.order_by(Message.id)
            if max:
                messages = messages.limit(max)
            resp = []
            for message in messages.all():
                entry = postline.Entry(
                    message=postline.parse_message(message.content),
                    key=message.id
                )
                resp.append(entry)
            return resp
