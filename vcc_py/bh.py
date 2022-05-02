# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from .constants import *

def do_lsse_bh(uid: int, msg_raw: bytes) -> None:
    """List the sessions"""
    for i in range(uid):
        print(msg_raw[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode())

def do_ls_bh(uid: int, msg_raw: bytes) -> None:
    """List the users"""
    for i in range(uid):
        print(msg_raw[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode())

def do_bh(type: int, uid: int, username: str, username_raw: bytes, msg: str, msg_raw: bytes) -> None:
    match type:
        case REQ.CTL_USRS:
            do_ls_bh(uid, msg_raw)
        case REQ.CTL_SESS:
            do_lsse_bh(uid, msg_raw)
        case _:
            raise Exception(f"Unknown response type: {type}, please update and retry")
