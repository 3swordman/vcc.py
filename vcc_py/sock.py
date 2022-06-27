# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 
from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, cast
import asyncio
import logging
import struct
import socket
import ipaddress

from .constants import *

# Can't import it directly, that will cause a circular import
if TYPE_CHECKING:
    from .plugin import Plugins

def bad_bytes(string: bytes) -> str:
    return string.decode(errors="ignore")

def bad_ntohl(value: int) -> int:
    try:
        return socket.ntohl(value)
    except OverflowError:
        return -1

class Connection:
    """A wrapper of socket which can recv or send messages and it's most method is asynchronous"""
    # plugs: Plugins
    def __init__(self, ip: str=VCC_DEFAULT_IP, port: int=VCC_PORT, usrname: str="", sess: int=0) -> None:
        ip_address = ipaddress.ip_address(ip)
        self.version = ip_address.version
        self.ip = ip
        self.port = port
        self._waiting_for_recv = False
        self.data = MyData(
            plugs = cast("Plugins", None),
            usrname = usrname,
            sess = sess,
            sess_list = [],
            level = 0,
            type = False
        )
    
    async def __aenter__(self) -> Connection:
        loop = asyncio.get_event_loop()
        if self.version == 4:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setblocking(False)
            self._sock.bind(("0.0.0.0", 0))
            await loop.sock_connect(self._sock, (self.ip, self.port))
        elif self.version == 6:
            self._sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self._sock.setblocking(False)
            self._sock.bind(("::", 0))
            await loop.sock_connect(self._sock, (self.ip, self.port, 0, 0))

        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    
    async def send(
        self, *, 
        magic: int = VCC_MAGIC, 
        type: int = REQ.MSG_SEND, 
        uid: int = 0, 
        session: int | None = None, 
        flags: int = 0, 
        usrname: str | None = None, 
        msg: str | bytes = "",
    ) -> None:
        loop = asyncio.get_event_loop()

        if session is None:
            session = self.data.sess

        if usrname is None:
            usrname = self.data.usrname
        logging.debug(f"msgic: {magic}, type: {type}, uid: {uid}, session: {session}, flags: {flags}, usrname: {usrname}, msg: {msg!r}")
        if isinstance(msg, str):
            msg += "\0"
            msg = msg.encode()
        await loop.sock_sendall(self._sock, struct.pack(
            VCC_REQUEST_FORMAT,
            socket.htonl(magic), 
            socket.htonl(type),
            socket.htonl(uid),
            socket.htonl(session),
            flags,
            (usrname + "\0").encode(),
            msg
        ))

    async def send_relay(self, *, magic: int = VCC_MAGIC_RL, uid: int = 0, session: int | None = None, usrname: str | None = None, msg: str, visible: str) -> None:
        loop = asyncio.get_event_loop()
        session = self.data.sess if session is None else session
        usrname = self.data.usrname if usrname is None else usrname
        length = struct.calcsize(VCC_RELAY_HEADER_FORMAT) + len(msg.encode()) + 1
    
        logging.debug(f"msgic: {magic}, uid: {uid}, session: {session}, length: {length}, usrname: {usrname}, msg: {msg}, visible: {visible}")
        await loop.sock_sendall(self._sock, struct.pack(
            VCC_RELAY_HEADER_FORMAT, 
            socket.htonl(magic), 
            socket.htonl(REQ.REL_MSG), 
            socket.htonl(length),
            socket.htonl(uid),
            socket.htonl(session), 
            usrname.encode() + b"\0",
            visible.encode() + b"\0"
        ))

        await loop.sock_sendall(self._sock, msg.encode() + b"\0")

    async def recv(self) -> tuple[RawRequest, Request] | tuple[RawRelay, Relay]:
        loop = asyncio.get_event_loop()

        raw_recv_data = await loop.sock_recv(self._sock, struct.calcsize(VCC_RELAY_HEADER_FORMAT))
        relay_header_data = RawRelayHeader(*struct.unpack(VCC_RELAY_HEADER_FORMAT, raw_recv_data))

        if socket.ntohl(relay_header_data.magic) != VCC_MAGIC:
            # handle a relay response
            logging.debug(f"raw relay header content: {repr(relay_header_data)}")
            size = bad_ntohl(relay_header_data.size) - struct.calcsize(VCC_RELAY_HEADER_FORMAT)
            logging.debug(f"{size}")
            raw_recv_data += await loop.sock_recv(self._sock, size)
            self._waiting_for_recv = False
            raw_relay_data = RawRelay(*struct.unpack(VCC_RELAY_HEADER_FORMAT + f"{size}s", raw_recv_data))
            magic = bad_ntohl(raw_relay_data.magic)
            type = bad_ntohl(raw_relay_data.type)
            uid = bad_ntohl(raw_relay_data.uid)
            session = bad_ntohl(raw_relay_data.session)
            usrname = raw_relay_data.usrname.decode(errors="ignore").split("\x00")[0]
            visible = raw_relay_data.visible.decode(errors="ignore").split("\x00")[0]
            msg = raw_relay_data.msg.decode(errors="ignore").split("\x00")[0]
            relay_tuple_data = Relay(magic, type, size, uid, session, usrname, visible, msg)
            logging.debug(f"raw relay content: {repr(raw_relay_data)}")
            logging.debug(f"relay content: {repr(relay_tuple_data)}")
            return raw_relay_data, relay_tuple_data
        
        # handle a normal response
        raw_recv_data += await loop.sock_recv(self._sock, REQ_SIZE - struct.calcsize(VCC_RELAY_HEADER_FORMAT))
        tuple_data = struct.unpack(VCC_REQUEST_FORMAT, raw_recv_data)
        self._waiting_for_recv = False
        raw_request = RawRequest(*tuple_data)
        decode_username = raw_request.usrname.decode(errors="ignore").split("\x00")[0]
        decode_msg = raw_request.msg.decode(errors="ignore").split("\x00")[0]
        request = Request(bad_ntohl(raw_request.magic), bad_ntohl(raw_request.type), bad_ntohl(raw_request.uid), bad_ntohl(raw_request.session), raw_request.flags, decode_username, decode_msg)
        logging.debug(f"raw request content: {repr(raw_request)}")
        logging.debug(f"request content: {repr(request)}")
        return raw_request, request
    
    async def wait_until_recv(self) -> None:
        self._waiting_for_recv = True
        while self._waiting_for_recv:
            await asyncio.sleep(0.1)
