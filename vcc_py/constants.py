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

from enum import IntEnum
from typing import NamedTuple, Final, TYPE_CHECKING

from dataclasses import dataclass

if TYPE_CHECKING:
    from .plugin import Plugins

VCC_MAGIC: Final = 0x01328e22
VCC_MAGIC_RL: Final = 0x01328e36

VCC_PORT: Final = 46
VCC_DEFAULT_IP: Final = "124.223.105.230"

REQ_SIZE: Final = 512
USERNAME_SIZE: Final = 32
PASSWD_SIZE: Final = 64
MSG_SIZE: Final = REQ_SIZE - 5 * 4 - USERNAME_SIZE

VCC_REQUEST_FORMAT: Final = f"<iiiii{USERNAME_SIZE}s{MSG_SIZE}s"
VCC_RELAY_HEADER_FORMAT: Final = f"<iiIii{USERNAME_SIZE}s{USERNAME_SIZE}s"

MSG_NEW_RELAY: Final = 0b1
MSG_NEW_ONLY_VISIBLE: Final = 0b10

FLAG_ENCRYPTED = 0b1

class REQ(IntEnum):
    MSG_SEND = 1
    MSG_NEW = 2
    CTL_USRS = 3
    CTL_LOGIN = 4
    CTL_NEWSE = 5
    CTL_SESS = 6
    CTL_JOINS = 7
    CTL_UINFO = 8
    SYS_SCRINC = 9
    REL_MSG = 10
    REL_NEW = 11
    CTL_IALOG = 12
    SYS_INFO = 13
    CTL_SENAME = 14
    CTL_QUITS = 15

class RawRequest(NamedTuple):
    magic: int
    type: int
    uid: int
    session: int
    flags: int
    usrname: bytes
    msg: bytes

class Request(NamedTuple):
    magic: int
    type: int
    uid: int
    session: int
    flags: int
    usrname: str
    msg: str

class RawRelayHeader(NamedTuple):
    magic: int
    type: int
    size: int
    uid: int
    session: int
    usrname: bytes
    visible: bytes

class RawRelay(NamedTuple):
    magic: int
    type: int
    size: int
    uid: int
    session: int
    usrname: bytes
    visible: bytes
    msg: bytes

class Relay(NamedTuple):
    magic: int
    type: int
    size: int
    uid: int
    session: int
    usrname: str
    visible: str
    msg: str

@dataclass
class MyData:
    plugs: Plugins
    usrname: str
    sess: int
    sess_list: list[str]
    level: int
    type: bool
    
class ExitError(Exception):
    pass
