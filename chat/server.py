from typing import Dict, Optional, List, Set
from websockets.asyncio.server import serve
from websockets import ServerConnection
import asyncio
import json
from enum import Enum
from constants import Header, Message, deserialize, serialize 
from websockets.exceptions import ConnectionClosedOK
import bisect


class WSPeer():
    def __init__(self, conn: ServerConnection, connId):
        self.conn = conn
        self.connId = connId
    async def send(self, message: str):
        await self.conn.send(message)
    async def recv(self):
        data = await self.conn.recv(1024)
        return data

users : Dict[str, List[WSPeer]] = {}

older_messages : Dict[str, List[Message]]= {}

def remove(connId, group):
    if users.get(group):
        users[group] = [peer for peer in users.get(group) if peer.connId != connId]
    else:
        del users[group]

def parse_data(data: str) -> Message:
    return json.loads(data)

async def handleClient(conn: ServerConnection):
    
    to_remove_from_group =""
    to_remove_conn_Id = ""
    try:
        async for data in conn:
            print(data)
            message = deserialize(data)
            print(message.header)
            if message.header == Header.JoinHeader:
                connId = message.connId
                if users.get(message.group):
                    if all(peer.connId != message.connId for peer in users.get(message.group)):
                        users.get(message.group).append(WSPeer(conn, connId=message.connId))
                elif not users.get(message.group):
                    users[message.group] = list()
                    users[message.group].append(WSPeer(conn, message.connId))    
                # check if the peer is not in the group
                

                if older_messages.get(message.group) is None:
                    print(users)
                    continue
                for message in older_messages.get(message.group):
                    for ws in users.get(message.group):
                        if ws.conn == conn:
                            try:
                                print("sending older messages")
                                await ws.send(serialize(message))
                                print("sent older messages")
                            except ConnectionClosedOK as e:
                                print('connected closed ', e)            
                print(users)
            elif message.header == Header.ChatHeader:
                if not older_messages.get(message.group):
                    older_messages[message.group] = list()
                bisect.insort(older_messages[message.group], message)
                for ws in users.get(message.group):
                    if ws.conn != conn:
                        try:
                            print("sending")
                            await ws.send(serialize(message))
                            print('sent')
                        except ConnectionClosedOK as e:
                            print('connected closed ', e)
            elif message.header == Header.CloseHeader:
                to_remove_conn_Id = message.connId
                to_remove_from_group = message.group
                
    except ConnectionClosedOK as e:
        print('connected closed with connId: ', connId)
    finally:
        remove(to_remove_conn_Id, to_remove_from_group)
        print(users)
    
from time import time

async def main(): 
    print(time())
    async with serve(handleClient, host='localhost', port=7000) as server:
        await server.serve_forever()


asyncio.run(main())