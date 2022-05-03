# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

import asyncio
from optparse import Option
import struct
import socket
from typing import Optional

from .constants import *

def bad_str(string: str) -> str:
    return repr(string)[1:-1]

def bad_bytes(string: bytes) -> str:
    return repr(string)[2:-1]

def bad_ntohl(value: int) -> int:
    try:
        return socket.ntohl(value)
    except OverflowError:
        return -1

class AsyncConnection:
    """A wrapper of socket which can recv or send messages and it's most method is asynchronous"""
    def __init__(self, ip: str=VCC_DEFAULT_IP, port: int=VCC_PORT, usrname: str="", sess: int=0) -> None:
        """It will only save informations, you must call init function"""
        self.ip = ip
        self.port = port
        self.usrname = usrname
        self._waiting_for_recv = False
        self.sess = sess
        self.level = 0
    
    async def init(self) -> "AsyncConnection":
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.bind(("0.0.0.0", 0))
        loop = asyncio.get_event_loop()
        await loop.sock_connect(self._sock, (self.ip, self.port))
        return self

    
    async def send(
        self, *, 
        magic: int = VCC_MAGIC, 
        type: int = REQ.MSG_SEND, 
        uid: int = 0, 
        session: Optional[int] = None, 
        flags: int = 0, 
        usrname: Optional[str] = None, 
        msg: str = ""
    ) -> None:
        loop = asyncio.get_event_loop()

        if session is None:
            session = self.sess

        if usrname is None:
            usrname = self.usrname
        
        await loop.sock_sendall(self._sock, struct.pack(
            VCC_REQUEST_FORMAT,
            socket.htonl(magic), 
            socket.htonl(type),
            socket.htonl(uid),
            socket.htonl(session),
            flags,
            (usrname + "\0").encode(),
            (msg + "\0").encode()
        ))

    async def recv(self) -> tuple[int, int, int, int, str, bytes, str, bytes]:
        loop = asyncio.get_event_loop()
        tuple_data = struct.unpack(VCC_REQUEST_FORMAT, await loop.sock_recv(self._sock, REQ_SIZE))
        self._waiting_for_recv = False
        magic: int
        type: int
        uid: int
        session: int
        flags: int
        usrname: bytes
        msg: bytes
        magic, type, uid, session, flags, usrname, msg = tuple_data
        try:
            decode_username = usrname.decode().split("\x00")[0]
        except UnicodeDecodeError:
            decode_username = bad_bytes(usrname.split(b"\x00")[0])
        try:
            decode_msg = msg.decode().split("\x00")[0]
        except UnicodeDecodeError:
            decode_msg = bad_bytes(msg.split(b"\x00")[0])
        if socket.ntohl(magic) != VCC_MAGIC:
            raise Exception("Incorrect magin number")
        return bad_ntohl(type), bad_ntohl(uid), bad_ntohl(session), flags, decode_username, usrname, decode_msg, msg
    
    async def wait_until_recv(self) -> None:
        self._waiting_for_recv = True
        while self._waiting_for_recv:
            await asyncio.sleep(0.1)
