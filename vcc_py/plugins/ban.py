# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from vcc_py.plugin import Plugin
from vcc_py.sock import Connection
from vcc_py.constants import Request

# Well, a bad way to ignore the Unbound, you can ignore it if you don't want to use typing
plugin: Plugin = globals()["plugin"]

ban_list: set[str] = set()

@plugin.register_recv_hook
def _(a: Request) -> Request | None:
    if a.usrname in ban_list:
        return None
    return a

@plugin.register_cmd("-ban")
async def _(conn: Connection, args: list[str]) -> None:
    """Ban someone so you won't receive messages from him/her"""
    if args:
        ban_people = args[0]
    else:
        ban_people = input("Enter the people you would like to ban: ")
    ban_list.add(ban_people)

@plugin.register_cmd("-unban")
async def _(conn: Connection, args: list[str]) -> None:
    """Unban someone so you will be able to receive more messages from him/her"""
    if args:
        unban_people = args[0]
    else:
        unban_people = input("Enter the people you would like to unban: ")
    ban_list.discard(unban_people)


