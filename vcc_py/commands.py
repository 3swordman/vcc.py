# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from typing import Callable, Awaitable, NoReturn, Any, Mapping
import sys

from . import pretty

from .sock import AsyncConnection as Connection
from .constants import *

async def do_cmd_currs(conn: Connection) -> None:
    """Get current session id"""
    print(conn.sess)

async def do_cmd_swtch(conn: Connection) -> None:
    """Switch session"""
    print(f"Old session id: {conn.sess}")
    conn.sess = int(input("New session id: "))
    # join session
    await conn.send(type=REQ.CTL_JOINS, usrname=conn.usrname, session=conn.sess)

async def do_cmd_newse(conn: Connection) -> None:
    """Create a new session"""
    await conn.send(type=REQ.CTL_NEWSE, usrname=conn.usrname, msg=input("Name of new session: "))

async def do_cmd_lsse(conn: Connection) -> None:
    """List the sessions"""
    await conn.send(type=REQ.CTL_SESS, uid=0)
    await conn.wait_until_recv()

async def do_cmd_help(conn: Connection) -> None:
    """Show information about every message. """
    for name in do_cmd_map:
        func = do_cmd_map[name]
        print(f"{name + ': ':<8}{func.__doc__}")

async def do_cmd_cqd(conn: Connection) -> None:
    """Send a "cqd", that's an interesting thing"""
    await conn.send(type=REQ.MSG_SEND, usrname=conn.usrname, msg="CQD")

async def do_cmd_quit(conn: Connection) -> NoReturn:
    """Disconnect to server and exit vcc"""
    print("bye.")
    sys.exit(0)

async def do_cmd_incr(conn: Connection) -> None:
    """Increase the number of messages"""
    username = input("username: ")
    incr = int(input("increment: "))
    await conn.send(type=REQ.SYS_SCRINC, usrname=username, session=incr)
    await conn.wait_until_recv()

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
    await conn.wait_until_recv()

async def do_cmd_uinfo(conn: Connection) -> None:
    """Get user information"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=input("Username: "))
    await conn.wait_until_recv()

async def do_cmd_lself(conn: Connection) -> None:
    """Reload information of myself"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=conn.usrname)
    await conn.wait_until_recv()

def is_banned(user: str) -> bool:
    """Get if someone is banned"""
    return user in ban_list

do_cmd_map: Mapping[str, Callable[[Connection], Awaitable[None | NoReturn]]] = {
    "-help": do_cmd_help,
    "-quit": do_cmd_quit,
    "-ls": do_cmd_ls,
    "-newse": do_cmd_newse,
    "-currs": do_cmd_currs,
    "-swtch": do_cmd_swtch,
    "-lsse": do_cmd_lsse,
    "-uinfo": do_cmd_uinfo,
    "-lself": do_cmd_lself,
    "-incr": do_cmd_incr,
    "-cqd": do_cmd_cqd,
    "-ban": do_cmd_ban,
    "-unban": do_cmd_unban
    # Encrypt
    # Plugin apis (won't be implemented)
}

async def do_cmd(string: str, conn: Connection) -> None:
    """Run a command"""
    command = string.split(" ", 1)[0]
    try:
        await do_cmd_map[command](conn)
    except KeyError:
        print(f"Unknown command \"{command}\"", file=sys.stderr)
