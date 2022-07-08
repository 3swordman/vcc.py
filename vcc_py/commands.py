# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from typing import Callable, Awaitable
import sys

from .sock import Connection
from .constants import *
from .pretty import help_line, prompt, show_msg

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
            print(f"No documentation for command \"{name}\"", file=sys.stderr)
            continue
        help_line(name, func.__doc__)

async def do_cmd_quit(conn: Connection, args: list[str]) -> None:
    """Disconnect to server and exit vcc"""
    print("bye.")
    raise ExitError()

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

async def do_cmd_ls(conn: Connection, args: list[str]) -> None:
    """List the users or sessions"""
    match args:
        case ["-s" | "--session" | "s" | "session"]:
            await conn.send(type=REQ.CTL_SESS, uid=0)
            await conn.wait_until_recv()
        case ["-u" | "--user" | "u" | "user"] | []:
            await conn.send(type=REQ.CTL_USRS, uid=0)
            await conn.wait_until_recv()
        case _:
            pass

async def do_cmd_uinfo(conn: Connection, args: list[str]) -> None:
    """Get user information"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=input("Username: ") if not args else args[0])
    await conn.wait_until_recv()

async def do_cmd_lself(conn: Connection, args: list[str]) -> None:
    """Reload information of myself"""
    await conn.send(type=REQ.CTL_UINFO, uid=0, msg=conn.data.usrname)
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

async def do_cmd_rl(conn: Connection, args: list[str]) -> None:
    """Send a "user-to-visible" message or a message containing -"""
    if not args:
        print("This command required at least an argument")
        return
    visible = args[0]
    args.pop(0)

    msg = " ".join(args)
    
    await conn.send_relay(msg=msg, visible="" if visible == "-" else visible)
    show_msg(conn.data.usrname, msg, conn.data.sess)

async def do_cmd_plg(conn: Connection, args: list[str]) -> None:
    """Plugin control"""
    match args:
        case ["-i" | "--install" | "i" | "install", name]:
            try:
                await conn.data.plugs.add_plugin(name)
            except ImportError:
                print("no such plugin")
        case ["-l" | "--list" | "ls" | "list"]:
            for module in conn.data.plugs.modules:
                if module["__package__"] is None:
                    continue
                print(module["__name__"].replace(module["__package__"], "")[1:])
        case _:
            print("usage: -plg [-i|-l|--install|--list|i|ls|install|list] [name]")

async def get_id_by_name(conn: Connection, name: str) -> int:
    if name in conn.data.sess_list:
        return conn.data.sess_list.index(name) + 1
    else:
        conn.data.type = True
        await conn.send(type=REQ.CTL_SESS, uid=0)
        await conn.wait_until_recv()
        if name in conn.data.sess_list:
            return conn.data.sess_list.index(name) + 1
        else:
            return -1

async def do_cmd_sess(conn: Connection, args: list[str]) -> None:
    """Session control"""
    match args:
        case ["-n" | "--new" | "n" | "new", name]:
            await conn.send(type=REQ.CTL_NEWSE, usrname=name)
        case ["-c" | "--curr" | "--current" | "c" | "curr" | "current"]:
            print(conn.data.sess)
        case ["-s" | "--switch" | "s" | "switch", id_]:
            id = int(id_)
            print(f"Old session id: {conn.data.sess}")
            conn.data.sess = id
            await conn.send(type=REQ.CTL_JOINS, session=id)
        case ["-p" | "--name" | "p" | "na" | "name", name]:
            # who knows what "-p" really means?
            sid = int(name)
            await conn.send(type=REQ.CTL_SENAME, session=sid)
            await conn.wait_until_recv()
        case ["-i" | "--id" | "i" | "id", name]:
            if (id := await get_id_by_name(conn, name)) == -1:
                print("No such session")
            else:
                print(id)
        case ["-j" | "--join" | "j" | "join", name]:
            if (id := await get_id_by_name(conn, name)) == -1:
                print("No such session")
            else:
                conn.data.sess = id
                await conn.send(type=REQ.CTL_JOINS, usrname=conn.data.usrname, session=conn.data.sess)
        case ["-q" | "--quit" | "q" | "quit", id_]:
            id = int(id_)
            if conn.data.sess == id:
                conn.data.sess = 0
            await conn.send(type=REQ.CTL_QUITS, usrname=conn.data.usrname, session=id)
        case ["-l", "--list", "ls", "list"]:
            await conn.send(type=REQ.CTL_SESS, uid=0)
            await conn.wait_until_recv()
        case _:
            pass
    

# async def do_cmd_encry(conn: Connection, args: list[str]) -> None:
#     """Send an encrypted message"""
#     await conn.send(flags=FLAG_ENCRYPTED, msg=conn.data.crypt.encrypt(args[0].encode()))
    
    
do_cmd_map: dict[str, Callable[[Connection, list[str]], Awaitable[None]]] = {
    "-help": do_cmd_help,
    "-quit": do_cmd_quit,
    "-ls": do_cmd_ls,
    "-uinfo": do_cmd_uinfo,
    "-lself": do_cmd_lself,
    "-incr": do_cmd_incr,
    "-ml": do_cmd_ml,
    "-send": do_cmd_send,
    "-rl": do_cmd_rl,
    "-plg": do_cmd_plg,
    "-sess": do_cmd_sess,
    # "-encry": do_cmd_encry
}

async def do_cmd(string: str, conn: Connection) -> None:
    """Run a command"""
    split_list = string.split(" ")
    command = split_list[0]
    args = split_list[1:]
    try:
        await do_cmd_map[command](conn, args)
        prompt(conn.data.usrname, conn.data.sess, conn.data.level)
    except KeyError:
        print(f"Unknown command \"{command}\"", file=sys.stderr)

def new_commands(commands: dict[str, Callable[[Connection, list[str]], Awaitable[None]]]) -> None:
    do_cmd_map.update(commands)
