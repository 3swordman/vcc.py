# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

import struct
import socket
import collections
import logging

import constants

class Connection:
    def __init__(self, ip=constants.VCC_DEFAULT_IP, port=constants.VCC_PORT):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind(("0.0.0.0", 0))
        self._sock.connect((ip, port))
    
    def send(
        self, *, 
        magic: int = constants.VCC_MAGIC, 
        type: int = constants.REQ_MSG_SEND, 
        uid: int = 0, 
        session: int = 0, 
        flags: int = 0, 
        usrname: str = "", 
        msg: str = ""
    ):
        self._sock.send(struct.pack(
            constants.VCC_REQUEST_FORMAT,
            socket.htonl(magic), 
            socket.htonl(type),
            socket.htonl(uid),
            socket.htonl(session),
            flags,
            (usrname + "\0").encode(),
            (msg + "\0").encode()
        ))
    def recv(self):
        tuple_data = struct.unpack(constants.VCC_REQUEST_FORMAT, self._sock.recv(constants.REQ_SIZE))
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
        return socket.ntohl(type), socket.ntohl(uid), socket.ntohl(session), flags, usrname.decode(), msg.decode()