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
import argparse

from vcc_py.plugin import Plugin
from vcc_py.constants import *
from vcc_py.sock import Connection

# Designed for testing and debuging

plugin: Plugin = globals()["plugin"]

connection_list: list[Connection] = []

@plugin.register_cmd("-radd")
async def _(conn: Connection, args: list[str]) -> None:
    """Create new connections"""
    global connection_list
    count = int(args[0] if args else input("count: "))
    data = conn.data
    connection_list += list(await asyncio.gather(*[asyncio.create_task(Connection(conn.ip, conn.port, data.usrname, data.sess).__aenter__()) for _ in range(count)]))

@plugin.register_cmd("-rsend")
async def _(conn: Connection, args: list[str]) -> None:
    """Send messages"""
    print(args)
    parser = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    parser.add_argument("--magic", type=int, metavar="magic", default=VCC_MAGIC)
    parser.add_argument("--type", type=int, metavar="type", default=REQ.MSG_SEND)
    parser.add_argument("--uid", type=int, metavar="uid", default=0)
    parser.add_argument("--session", type=int, metavar="session", default=0)
    parser.add_argument("--flags", type=int, metavar="flags", default=0)
    parser.add_argument("--usrname", type=str, metavar="usrname", default=conn.data.usrname)
    parser.add_argument("--repeat", type=int, metavar="repeat", default=1)
    parser.add_argument(dest="msg", metavar="msg", nargs="?")
    args_ns = parser.parse_args(args)
    print(args_ns)
    await asyncio.gather(*[asyncio.create_task(i.send(
        magic = args_ns.magic,
        type = args_ns.type,
        uid = args_ns.uid,
        session = args_ns.uid,
        flags = args_ns.flags,
        usrname = args_ns.usrname,
        msg = args_ns.msg
    )) for i in connection_list for _ in range(args_ns.repeat)])






