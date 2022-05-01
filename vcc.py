#!/bin/python3
# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

import _thread as thread

import asyncio
import sys
from getpass import getpass
import argparse
import logging
import signal
from datetime import datetime

from sock import AsyncConnection
from constants import *
from commands import do_cmd
import pretty

async def ainput(*args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: input(*args, **kwargs))

def parse_args():
    parser = argparse.ArgumentParser(description="Talk with others using %(prog)s :)")
    parser.add_argument("-p", "--port", type=int, metavar="port", default=VCC_PORT, help="specified the port the server use (defualt: 46)")
    parser.add_argument("-u", "--user", type=str, metavar="username", help="the username you want to use")
    parser.add_argument(dest="ip", metavar="ip", nargs="?", default=VCC_DEFAULT_IP, help="the ip address of the server")
    return parser.parse_args()

async def recv_loop(conn: AsyncConnection):
    while True:
        type, uid, session, flags, usrname, msg = await conn.recv()
        if type == REQ_MSG_NEW:
            pretty.show_msg(usrname, msg, newlinefirst=True)

async def request_recv_loop(conn: AsyncConnection):
    while True:
        await asyncio.sleep(1)
        await conn.send(type=REQ_MSG_NEW)

async def input_send_loop(conn: AsyncConnection):
    while True:
        pretty.prompt(curr_usrname)
        msg = await ainput("")
        if not msg:
            continue
        if msg[0] == "-":
            await do_cmd(msg, conn)
            continue
        await conn.send(
            type=REQ_MSG_SEND,
            usrname=curr_usrname,
            msg=msg
        )
        pretty.show_msg(curr_usrname, msg)

connection: AsyncConnection

async def main():
    global connection
    connection = await AsyncConnection(args.ip, args.port, curr_usrname).init()
    await connection.send(
        type=REQ_CTL_LOGIN,
        usrname=curr_usrname,
        msg=password
    )
    type, uid, *_ = await connection.recv()
    if type != REQ_CTL_LOGIN:
        raise Exception("Invalid response received")
    if not uid:
        raise Exception("login failed: wrong password or user doesn't exists")
    print("ready.")
    await asyncio.gather(
        asyncio.create_task(recv_loop(connection)),
        asyncio.create_task(request_recv_loop(connection)),
        asyncio.create_task(input_send_loop(connection))
    )
    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    args = parse_args()
    if not (sys.stdout.isatty() and sys.stderr.isatty() and sys.stdin.isatty()):
        logging.error("stdout, stderr or stdin is redirected. ")
        sys.exit(1)
    curr_usrname: str = args.user if args.user else input("login as: ")
    password = getpass("password: ")
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(e)
        sys.exit(1)
