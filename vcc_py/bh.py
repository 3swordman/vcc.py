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
import logging

from .constants import *

def do_lsse_bh(req: Request, req_raw: RawRequest, data: MyData) -> None:
    """List the sessions"""
    logging.debug(f"Lsse bh: score: {req.uid}")
    data.sess_list = [req_raw.msg[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode().split("\0", 2)[0] for i in range(req.uid)]
    if not data.type:
        print("\n".join(data.sess_list))
    data.type = False

USER_FORMAT = f"<ii{USERNAME_SIZE}s{PASSWD_SIZE}s{MSG_SIZE - USERNAME_SIZE - PASSWD_SIZE - 2 * 4}x"

def do_uinfo_bh(req: Request, req_raw: RawRequest, data: MyData) -> None:
    """Show user info"""
    logging.debug(f"Uinfo bh: uid: {req.uid}")
    if req.uid == -1:
        print("User not found")
        return
    score: int
    level: int
    username: bytes
    score, level, username, _ = struct.unpack(USER_FORMAT, req_raw.msg)
    logging.debug(f"Uinfo bh: score (not ntohl): {score}")
    logging.debug(f"Uinfo bh: level (not ntohl): {level}")
    if score < 0 or level < 0:
        print("User not found")
        return
    if data.usrname == username.decode().split("\x00")[0]:
        print(f"level of yourself: {socket.ntohl(level)}")
        data.level = socket.ntohl(level)
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

def do_ls_bh(req: Relay, req_raw: RawRelay) -> None:
    """List the users"""
    logging.debug(f"Number of the response of '-ls': {req.uid}")
    for i in range(req.uid):
        print(req_raw.msg[i * USERNAME_SIZE: (i + 1) * USERNAME_SIZE].decode())

def do_sename_bh(req: Request) -> None:
    if req.session == -1:
        print("No such session")
        return
    print(f"{req.session}: {req.msg}")

def do_bh(req: Request | Relay, req_raw: RawRequest | RawRelay, data: MyData) -> None:
    logging.debug(f"Message type: {req.type}")
    if not (isinstance(req, Request) and isinstance(req_raw, RawRequest)) and not (isinstance(req, Relay) and isinstance(req_raw, RawRelay)):
        raise Exception(f"Internal error")
    if isinstance(req, Request) and isinstance(req_raw, RawRequest):
        match req.type:
            case REQ.CTL_SESS:
                do_lsse_bh(req, req_raw, data)
            case REQ.CTL_UINFO:
                do_uinfo_bh(req, req_raw, data)
            case REQ.SYS_SCRINC:
                do_incr_bh(req)
            case REQ.CTL_SENAME:
                do_sename_bh(req)
            case _:
                raise Exception(f"Unknown response type: {req.type}, please update and retry")
    elif isinstance(req, Relay) and isinstance(req_raw, RawRelay):
        match req.type:
            case REQ.CTL_USRS:
                do_ls_bh(req, req_raw)
            case _:
                raise Exception(f"Unknown response type: {req.type}, please update and retry")

