# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from typing import Callable, Coroutine
import sys

import pretty

from sock import AsyncConnection as Connection
from constants import *

async def do_cmd_help(conn: Connection):
    for name in do_cmd_map:
        _, msg = do_cmd_map[name]
        print(f"{name + ': ':<8}{msg}")

async def do_cmd_cqd(conn: Connection):
    await conn.send(type=REQ_MSG_SEND, usrname=conn.usrname, msg="CQD")

async def do_cmd_quit(conn: Connection):
    print("bye.")
    sys.exit(0)

do_cmd_map: "dict[str, tuple[Callable[[Connection], Coroutine], str]]" = {
    "-help": (do_cmd_help, "Show information about every message. "),
    "-cqd": (do_cmd_cqd, "Raise CQD. "),
    "-quit": (do_cmd_quit, "Disconnect to server and exit vcc. "),
    "-exit": (do_cmd_quit, "Alias of -quit. ")
}

async def do_cmd(string: str, conn: Connection):
    command = string.split(" ", 1)[0]
    try:
        func, help_msg = do_cmd_map[command]
        await func(conn)
    except KeyError:
        print(f"Unknown command \"{command}\"", file=sys.stderr)