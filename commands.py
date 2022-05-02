# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from typing import Callable, Coroutine, NoReturn, Any, Union, Mapping
import sys

import pretty

from sock import AsyncConnection as Connection
from constants import *

async def do_cmd_help(conn: Connection) -> None:
    """Print help information from somebody"""
    for name in do_cmd_map:
        _, msg = do_cmd_map[name]
        print(f"{name + ': ':<8}{msg}")

async def do_cmd_cqd(conn: Connection) -> None:
    """Send a "cqd", that's an interesting thing"""
    await conn.send(type=REQ.MSG_SEND, usrname=conn.usrname, msg="CQD")

async def do_cmd_quit(conn: Connection) -> NoReturn:
    """Disconnect to server and exit vcc"""
    print("bye.")
    sys.exit(0)

ban_list: set[str] = set()

async def do_cmd_ban(conn: Connection) -> None:
    """Ban someone so you won't receive messages from him/her"""
    ban_list.add(input("Enter the people you would like to ban: "))

async def do_cmd_unban(conn: Connection) -> None:
    """Unban someone so you will be able to receive more messages from him/her"""
    ban_list.discard(input("Enter the people you would like to unban: "))

async def do_cmd_ls(conn: Connection) -> None:
    """List the users"""
    await conn.send(type=REQ.CTL_USRS, uid=0)

def is_banned(user: str) -> bool:
    """Get if someone is banned"""
    return user in ban_list

do_cmd_map: Mapping[str, tuple[Callable[[Connection], Coroutine[Any, Any, Union[None, NoReturn]]], str]] = {
    "-help": (do_cmd_help, "Show information about every message. "),
    "-cqd": (do_cmd_cqd, "Raise CQD. "),
    "-quit": (do_cmd_quit, "Disconnect to server and exit vcc. "),
    "-exit": (do_cmd_quit, "Alias of -quit. "),
    "-ban": (do_cmd_ban, "Don't receive more messages from somebody. "),
    "-unban": (do_cmd_unban, "Receive more messages from somebody. "),
    "-ls": (do_cmd_ls, "List the users. ")
}

async def do_cmd(string: str, conn: Connection) -> None:
    """Run a command"""
    command = string.split(" ", 1)[0]
    try:
        func, help_msg = do_cmd_map[command]
        await func(conn)
    except KeyError:
        print(f"Unknown command \"{command}\"", file=sys.stderr)
