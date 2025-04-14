import pytest
from websockets.asyncio.client import connect
import json
from enum import Enum
from typing import Optional
class Header(Enum):
    JoinHeader = 'join'
    ChatHeader = 'chat'
    CloseHeader = 'close'

class Message:
    header: Header
    group: str
    message: Optional[str]
    connId : Optional[str]
    def __init__(self, header, grp: str, message: Optional[str] = None, connId: Optional[str] = None):
        self.header = header
        self.group = grp
        self.message = message
        self.connId = connId
import json

def serialize(message: Message) -> str:
    if message.header == Header.JoinHeader:
        header = 'join'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group, "connId" : message.connId}
        return json.dumps(data)
    if message.header == Header.ChatHeader:
        header = 'chat'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group}
        return json.dumps(data)
    if message.header == Header.CloseHeader:
        header = 'close'
        value = message.message
        data = { "header" : header, "value" : value, "group" : message.group, "connId" : message.connId}
        return json.dumps(data)

def deserialize(s: str) -> Message:
    data = json.loads(s)
    if data['header'] == 'join':
        return Message(header = Header.JoinHeader, grp=data['group'] , message=data['value'], connId=data['connId'])
    if data['header'] == 'chat':
        return Message(header = Header.ChatHeader, grp = data['group'], message=data['value'])
    if data['header'] == 'close':
        return Message(header = Header.CloseHeader, grp = data['group'], message=data['value'], connId=data['connId'])
import asyncio

async def open_connection():
    return await connect('ws://localhost:7000')



async def receive_loop(client, idx):
    try:
        while True:
            msg = await asyncio.wait_for(client.recv(), timeout=5.0)
            print(f"client {idx} received: {msg}")
    except asyncio.TimeoutError:
        print(f"client {idx} done receiving (timeout).")
    except Exception as e:
        print(f"client {idx} error: {e}")

async def test_realtime_grp_chat():
    print("here")
    clients = await asyncio.gather(*[open_connection() for _ in range(5)])
    print(clients)

    try:
        for (i, client) in enumerate(clients):
            join_data = serialize(Message(header=Header.JoinHeader, grp='grp1', connId=f'conn{i}'))
            await client.send(join_data)
            chat_data = serialize(Message(header=Header.ChatHeader, grp='grp1', connId=f'conn{i}', message=f'hello {i}'))
            await client.send(chat_data)

        # 🔄 Start a receive task per client
        receive_tasks = [
            asyncio.create_task(receive_loop(client, i))
            for i, client in enumerate(clients)
        ]

        # Let them run for a few seconds (simulate active chat window)
        await asyncio.sleep(10)

        # ⛔ Cancel all receive tasks after sleep
        for task in receive_tasks:
            task.cancel()

    finally:
        for (i, client) in enumerate(clients):
            close_data = serialize(Message(header=Header.CloseHeader, grp='grp1', connId=f'conn{i}'))
            await client.send(close_data)
            await client.close()


asyncio.run(test_realtime_grp_chat())
# @pytest.mark.asyncio
# async def test_join_message(websocket):
#     data = serialize(Message(header=Header.JoinHeader, grp='grp1'))
#     print(data)
#     await websocket.send(data)
#     #message = await websocket.recv(1024)
#     #print(message)
    

# @pytest.mark.asyncio
# async def test_chat_message(websocket):
#     data = serialize(Message(header = Header.ChatHeader, grp='grp1', message='hello'))
#     print("here" , data)
#     await websocket.send(data)
#     message = await websocket.recv(1024)
#     print(message)