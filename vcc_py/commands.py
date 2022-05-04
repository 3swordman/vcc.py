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
from .pretty import help_line

async def do_cmd_currs(conn: Connection, args: list[str]) -> None:
    """Get current session id"""
    print(conn.sess)

async def do_cmd_swtch(conn: Connection, args: list[str]) -> None:
    """Switch session"""
    print(f"Old session id: {conn.sess}")
    conn.sess = int(input("New session id: ") if not args else args[0])
    # join session
    await conn.send(type=REQ.CTL_JOINS, usrname=conn.usrname, session=conn.sess)

async def do_cmd_newse(conn: Connection, args: list[str]) -> None:
    """Create a new session"""
    await conn.send(type=REQ.CTL_NEWSE, usrname=conn.usrname, msg=input("Name of new session: "))

async def do_cmd_lsse(conn: Connection, args: list[str]) -> None:
    """List the sessions"""
    await conn.send(type=REQ.CTL_SESS, uid=0)
    await conn.wait_until_recv()

async def do_cmd_help(conn: Connection, args: list[str]) -> None:
    """Show information about every message. """
    if args:
        try:
            func = do_cmd_map[args[0]]
        except KeyError:
            print(f"Unknown command \"{args[0]}\"", file=sys.stderr)
            return
        
        if func.__doc__ is None:
            # for type checker
            print(f"No documentation for command \"{args[0]}\"", file=sys.stderr)
            return
        
        help_line(args[0], func.__doc__)
        return

    for name in do_cmd_map:
        func = do_cmd_map[name]
        if func.__doc__ is None:
            # for type checker
            print(f"No documentation for command \"{args[0]}\"", file=sys.stderr)
            continue
        help_line(name, func.__doc__)

async def do_cmd_cqd(conn: Connection, args: list[str]) -> None:
    """Send a "cqd", that's an interesting thing"""
    await conn.send(type=REQ.MSG_SEND, usrname=conn.usrname, msg="CQD")

async def do_cmd_quit(conn: Connection, args: list[str]) -> NoReturn:
    """Disconnect to server and exit vcc"""
    print("bye.")
    sys.exit(0)

async def do_cmd_incr(conn: Connection, args: list[str]) -> None:
    """Increase the number of messages"""
    if len(args) == 2:
        username = args[0]
        incr = int(args[1])
    else:
        username = input("username: ")
        incr = int(input("increment: "))
    await conn.send(type=REQ.SYS_SCRINC, usrname=username, session=incr)
    await conn.wait_until_recv()

ban_list: set[str] = set()

async def do_cmd_ban(conn: Connection, args: list[str]) -> None:
    """Ban someone so you won't receive messages from him/her"""
    if args:
        ban_people = args[0]
    else:
        ban_people = input("Enter the people you would like to ban: ")
    ban_list.add(ban_people)

async def do_cmd_unban(conn: Connection, args: list[str]) -> None:
    """Unban someone so you will be able to receive more messages from him/her"""
    if args:
        unban_people = args[0]
    else:
        unban_people = input("Enter the people you would like to inban: ")
    ban_list.discard(unban_people)

async def do_cmd_ls(conn: Connection, args: list[str]) -> None:
    """List the users"""
    await conn.send(type=REQ.CTL_USRS, uid=0)
    await conn.wait_until_recv()

async def do_cmd_uinfo(conn: Connection, args: list[str]) -> None:
    """Get user information"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=input("Username: ") if not args else args[0])
    await conn.wait_until_recv()

async def do_cmd_lself(conn: Connection, args: list[str]) -> None:
    """Reload information of myself"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=conn.usrname)
    await conn.wait_until_recv()

async def do_cmd_ml(conn: Connection, args: list[str]) -> None:
    """Run commands in multi-line"""
    print("Type finish to finish it.")
    lines: list[str] = []
    try:
        while ((line := input(">>> ")) != "finish"):
            lines.append(line)
    except EOFError:
        pass
    for line in lines:
        split_list = line.split(" ")
        command = "-" + split_list[0]
        args = split_list[1:]
        try:
            await do_cmd_map[command](conn, args)
        except KeyError:
            print(f"Unknown command \"{command}\"", file=sys.stderr)
            return

async def do_cmd_send(conn: Connection, args: list[str]) -> None:
    """Send a message (designed for ml, slient for sender)"""
    await conn.send(
        type=REQ.MSG_SEND,
        msg=args[0] if args else input("Message: ")
    )

def is_banned(user: str) -> bool:
    """Get if someone is banned"""
    return user in ban_list

do_cmd_map: Mapping[str, Callable[[Connection, list[str]], Awaitable[None | NoReturn]]] = {
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
    "-unban": do_cmd_unban,
    "-ml": do_cmd_ml,
    "-send": do_cmd_send
    # Encrypt
    # Plugin apis (won't be implemented, or it might be implemented in a different way)
}

async def do_cmd(string: str, conn: Connection) -> None:
    """Run a command"""
    split_list = string.split(" ")
    command = split_list[0]
    args = split_list[1:]
    try:
        await do_cmd_map[command](conn, args)
    except KeyError:
        print(f"Unknown command \"{command}\"", file=sys.stderr)
