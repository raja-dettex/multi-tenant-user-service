from enum import Enum
from typing import Optional
from time import time
class Header(Enum):
    JoinHeader = 'join'
    ChatHeader = 'chat'
    CloseHeader = 'close'

class Message:
    header: Header
    group: str
    message: Optional[str]
    connId : Optional[str]
    timestamp: Optional[float]
    def __init__(self, header, grp: str, message: Optional[str] = None, connId: Optional[str] = None, timestamp:Optional[float] = None ):
    
        self.header = header
        self.group = grp
        self.message = message
        self.connId = connId
        self.timestamp = timestamp
    def __lt__(self, other):
        # None is treated as "inf" (latest possible timestamp)
        return (self.timestamp or float('inf')) < (other.timestamp or float('inf'))

    def __repr__(self):
        return f"<Message ts={self.timestamp}>"
import json

def serialize(message: Message) -> str:
    if message.header == Header.JoinHeader:
        header = 'join'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group, "connId" : message.connId, "timestamp": message.timestamp}
        return json.dumps(data)
    if message.header == Header.ChatHeader:
        header = 'chat'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group, "connId": message.connId, "timestamp": message.timestamp}
        return json.dumps(data)
    if message.header == Header.CloseHeader:
        header = 'close'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group, "connId" : message.connId, "timestamp": message.timestamp}
        return json.dumps(data)

def deserialize(s: str) -> Message:
    data = json.loads(s)
    if data['header'] == 'join':
        return Message(header = Header.JoinHeader, grp=data['group'] , message=data['value'], connId=data['connId'], timestamp=data['timestamp'])
    if data['header'] == 'chat':
        return Message(header = Header.ChatHeader, grp = data['group'], message=data['value'], connId=data['connId'], timestamp=data['timestamp'])
    if data['header'] == 'close':
        return Message(header = Header.CloseHeader, grp = data['group'], message=data['value'], connId=data['connId'], timestamp=data['timestamp'])