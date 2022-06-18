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

def init(plugin: Plugin) -> None:
    @plugin.register_cmd("-cqd")
    async def _(conn: Connection, args: list[str]) -> None:
        """Send a "cqd", that's an interesting thing"""
        await conn.send(msg="CQD")


