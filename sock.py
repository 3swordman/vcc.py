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
import struct
import socket
import collections
import logging

import constants

class AsyncConnection:
    """A wrapper of socket which can recv or send messages and it's most method is asynchronous"""
    # The init method actually is init
    def __init__(self, ip: str=constants.VCC_DEFAULT_IP, port: int=constants.VCC_PORT, usrname: str="") -> None:
        """It will only save informations, you must """
        self.ip = ip
        self.port = port
        self.usrname = usrname
    
    async def init(self) -> "AsyncConnection":
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setblocking(False)
        self._sock.bind(("0.0.0.0", 0))
        loop = asyncio.get_event_loop()
        await loop.sock_connect(self._sock, (self.ip, self.port))
        return self

    
    async def send(
        self, *, 
        magic: int = constants.VCC_MAGIC, 
        type: int = constants.REQ.MSG_SEND, 
        uid: int = 0, 
        session: int = 0, 
        flags: int = 0, 
        usrname: str = "", 
        msg: str = ""
    ) -> None:
        loop = asyncio.get_event_loop()
        await loop.sock_sendall(self._sock, struct.pack(
            constants.VCC_REQUEST_FORMAT,
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
        tuple_data = struct.unpack(constants.VCC_REQUEST_FORMAT, await loop.sock_recv(self._sock, constants.REQ_SIZE))
        magic: int
        type: int
        uid: int
        session: int
        flags: int
        usrname: bytes
        msg: bytes
        magic, type, uid, session, flags, usrname, msg = tuple_data
        if socket.ntohl(magic) != constants.VCC_MAGIC:
            raise Exception("Incorrect magin number")
        return socket.ntohl(type), socket.ntohl(uid), socket.ntohl(session), flags, usrname.decode().split("\x00")[0], usrname, msg.decode().split("\x00", 1)[0], msg
