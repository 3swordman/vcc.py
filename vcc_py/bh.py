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

from .sock import AsyncConnection
from .constants import *

def do_lsse_bh(req: Request, req_raw: RawRequest) -> None:
    """List the sessions"""
    for i in range(req.uid):
        print(req_raw.msg[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode())

USER_FORMAT = f"<ii{USERNAME_SIZE}s{PASSWD_SIZE}s{MSG_SIZE - USERNAME_SIZE - PASSWD_SIZE - 2 * 4}x"

def do_uinfo_bh(req: Request, req_raw: RawRequest, conn: AsyncConnection) -> None:
    """Show user info"""
    if req.uid == -1:
        print("User not found")
        return
    score: int
    level: int
    username: bytes
    score, level, username, _ = struct.unpack(USER_FORMAT, req_raw.msg)
    if score < 0 or level < 0:
        print("User not found")
        return
    if conn.usrname == username.decode().split("\x00")[0]:
        print(f"level of yourself: {socket.ntohl(level)}")
        conn.level = socket.ntohl(level)
    else:
        print(f"{username.decode().split(chr(0))[0]}'s info: ")
        print("\tscore\tlevel")
        print(f"\t{socket.ntohl(score):<5}\t{socket.ntohl(level):<5}")

def do_incr_bh(req: Request) -> None:
    """Increase score"""
    if req.uid:
        print("Your operation is failed")
    else:
        print("You've completed it successfully")

def do_ls_bh(req: Request, req_raw: RawRequest) -> None:
    """List the users"""
    for i in range(req.uid):
        print(req_raw.msg[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode())

def do_bh(req: Request, req_raw: RawRequest, conn: AsyncConnection) -> None:
    match req.type:
        case REQ.CTL_USRS:
            do_ls_bh(req, req_raw)
        case REQ.CTL_SESS:
            do_lsse_bh(req, req_raw)
        case REQ.CTL_UINFO:
            do_uinfo_bh(req, req_raw, conn)
        case REQ.SYS_SCRINC:
            do_incr_bh(req)
        case _:
            raise Exception(f"Unknown response type: {req.type}, please update and retry")
