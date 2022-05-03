#!/bin/env python3
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
import sys
from getpass import getpass
import argparse
import logging
from typing import NoReturn

from .sock import AsyncConnection
from .constants import *
from .commands import do_cmd, is_banned
from .bh import do_bh, do_uinfo_bh
from . import pretty

async def ainput(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    def input_handler() -> str:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            return ""
    return await loop.run_in_executor(None, input_handler)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Talk with others using %(prog)s :)")
    parser.add_argument("-p", "--port", type=int, metavar="port", default=VCC_PORT, help="specified the port the server use (defualt: 46)")
    parser.add_argument("-u", "--user", type=str, metavar="username", help="the username you want to use")
    parser.add_argument(dest="ip", metavar="ip", nargs="?", default=VCC_DEFAULT_IP, help="the ip address of the server")
    return parser.parse_args()

async def recv_loop(conn: AsyncConnection) -> NoReturn:
    while True:
        type, uid, session, flags, usrname, usrname_raw, msg, msg_raw = await conn.recv()
        if is_banned(usrname):
            continue
        if type == REQ.MSG_NEW:
            if msg == "CQD":
                pretty.cqd(usrname)
            else:
                pretty.show_msg(usrname, msg, session, newlinefirst=True)
        else:
            do_bh(type, uid, usrname, usrname_raw, msg, msg_raw, conn.usrname, conn)

async def input_send_loop(conn: AsyncConnection) -> NoReturn:
    while True:
        pretty.prompt(curr_usrname, conn.sess, conn.level)
        msg = await ainput("")
        if not msg:
            continue
        if msg[0] == "-":
            await do_cmd(msg, conn)
            continue
        await conn.send(
            type=REQ.MSG_SEND,
            usrname=curr_usrname,
            msg=msg
        )
        pretty.show_msg(curr_usrname, msg, conn.sess)

connection: AsyncConnection
curr_usrname: str
args: argparse.Namespace
async def main() -> None:
    global args
    global curr_usrname
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    args = parse_args()
    if not (sys.stdout.isatty() and sys.stderr.isatty() and sys.stdin.isatty()):
        logging.error("stdout, stderr or stdin is redirected. ")
        sys.exit(1)
    curr_usrname = args.user if args.user else input("login as: ")
    logging.debug("got username")
    password = getpass("password: ")
    logging.debug("got password")
    global connection
    connection = await AsyncConnection(args.ip, args.port, curr_usrname).init()
    logging.debug("init the socket successful")
    await connection.send(
        type=REQ.CTL_LOGIN,
        usrname=curr_usrname,
        msg=password
    )
    logging.debug("send the login request")
    type, uid, *_ = await connection.recv()
    logging.debug("recv the login response")
    if type != REQ.CTL_LOGIN:
        raise Exception("Invalid response received")
    if not uid:
        raise Exception("login failed: wrong password or user doesn't exists")
    logging.debug("login successfully")
    print("ready.")
    runloop = asyncio.gather(
        asyncio.create_task(recv_loop(connection)),
        asyncio.create_task(input_send_loop(connection))
    )
    await connection.send(type=REQ.CTL_UINFO, uid=0, msg=connection.usrname)
    await runloop
    
def amain() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    amain()
