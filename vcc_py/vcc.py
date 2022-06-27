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
import os.path
import signal
import ipaddress
import socket
from types import FrameType
from typing import Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from .sock import Connection
from .constants import *
from .commands import do_cmd
from .bh import do_bh
from .plugin import Plugins
from . import pretty

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Talk with others using %(prog)s :)", prog="vcc")
    parser.add_argument("-p", "--port", type=int, metavar="port", default=VCC_PORT, help="specified the port the server use (defualt: 46)")
    parser.add_argument("-u", "--user", type=str, metavar="username", help="the username you want to use")
    parser.add_argument("-D", "--debug", action="store_true", help="enable debug mode")
    parser.add_argument(dest="ip", metavar="ip", nargs="?", default=VCC_DEFAULT_IP, help="the ip address of the server")
    return parser.parse_args()

async def recv_loop(conn: Connection, plugs: Plugins) -> None:
    try:
        while True:
            req_raw, req = await conn.recv()
            if isinstance(req_raw, RawRelay) and isinstance(req, Relay):
                flag = MSG_NEW_RELAY
                if req.uid:
                    flag |= MSG_NEW_ONLY_VISIBLE
                try:
                    do_bh(req, req_raw, conn.data)
                except Exception:
                    pretty.show_msg(req.usrname, req.msg, req.session, newlinefirst=True, flag=flag)
            else:
                assert isinstance(req_raw, RawRequest) and isinstance(req, Request)
                _req = plugs.recv_msg(req)
                if _req is None:
                    continue
                req = _req
                if req.type == REQ.MSG_NEW:
                    pretty.show_msg(req.usrname, req.msg, req.session, newlinefirst=True)
                else:
                    do_bh(req, req_raw, conn.data)
    except asyncio.CancelledError:
            return

async def input_send_loop(conn: Connection, plugs: Plugins, quit_func: Callable[[], bool]) -> None:
    session: PromptSession[str] = PromptSession()
    while True:
        pretty.prompt(curr_usrname, conn.data.sess, conn.data.level)
        try:
            msg = await session.prompt_async("", auto_suggest=AutoSuggestFromHistory())
        except asyncio.CancelledError:
            return
        except KeyboardInterrupt:
            continue
        except EOFError:
            quit_func()
            return
        _msg = plugs.send_msg(msg)
        if _msg is None:
            continue
        msg = _msg
        if not msg:
            continue
        if msg[0] == "-":
            try:
                await do_cmd(msg, conn)
            except ExitError:
                quit_func()
                return
            continue
        await conn.send(
            type=REQ.MSG_SEND,
            usrname=curr_usrname,
            msg=msg
        )
        pretty.show_msg(curr_usrname, msg, conn.data.sess)

connection: Connection
curr_usrname: str
args: argparse.Namespace

def get_username_and_password_or_session() -> tuple[str, str]:
    session_filename = "/var/run/intiauth-session"
    user_filename = "/var/run/intiauth-user"
    if os.path.isfile(session_filename) and os.path.isfile(user_filename) and sys.platform.startswith("win32"):
        with (
            open(session_filename) as session_file,
            open(user_filename) as user_file,
        ):
            session_text = session_file.read(64)
            curr_usrname = user_file.read(USERNAME_SIZE)
            return curr_usrname, session_text
    else:
        curr_usrname = args.user if args.user else input("login as: ")
        logging.debug("got username")
        password = getpass("password: ")
        logging.debug("got password")
        return curr_usrname, password
        

async def main() -> None:
    global args
    global curr_usrname
    global connection
    args = parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARN, format="%(levelname)s: %(message)s")
    if not (sys.stdout.isatty() and sys.stderr.isatty() and sys.stdin.isatty()):
        logging.error("stdout, stderr or stdin is redirected. ")
        sys.exit(1)

    ip: str
    try:
        ipaddress.ip_address(args.ip)
    except ValueError:
        try:
            ip = socket.gethostbyname(args.ip)
        except socket.gaierror:
            logging.error("not a valid ip or host. ")
            sys.exit(1)
    else:
        ip = args.ip
    
    curr_usrname, password = get_username_and_password_or_session()

    async with Connection(ip, args.port, curr_usrname) as connection:
        logging.debug("init the socket successfully")
        await connection.send(
            type=REQ.CTL_LOGIN,
            usrname=curr_usrname,
            msg=password
        )
        logging.debug("send the login request")
        _, (_, type, uid, *_) = await connection.recv()
        logging.debug("recv the login response")
        if type != REQ.CTL_LOGIN:
            raise Exception("Invalid response received")
        if not uid:
            raise Exception("login failed: wrong password or user doesn't exists")
        logging.debug("login successfully")
        async with Plugins(connection) as plugs:
            connection.data.plugs = plugs
            recv_loop_task = asyncio.create_task(recv_loop(connection, plugs))
            input_send_loop_task = asyncio.create_task(input_send_loop(connection, plugs, lambda: recv_loop_task.cancel()))
            def sigint_handler(sig: int, frame: FrameType | None) -> None:
                recv_loop_task.cancel()
                input_send_loop_task.cancel()
            signal.signal(signal.SIGINT, sigint_handler)
            runloop: asyncio.Future[tuple[None, None]] = asyncio.gather(
                recv_loop_task,
                input_send_loop_task
            )
            await connection.send(type=REQ.CTL_UINFO, uid=0, msg=connection.data.usrname)
            await runloop
    
def amain() -> None:
    asyncio.run(main())

if __name__ == "__main__":
    amain()
