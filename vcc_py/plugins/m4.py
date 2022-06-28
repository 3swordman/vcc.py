# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from subprocess import Popen, PIPE

import sys

from vcc_py.plugin import Plugin
from vcc_py.sock import Connection

plugin: Plugin = globals()["plugin"]

if sys.platform.startswith("win32"):
    exit()
loaded = False
command = ""
@plugin.register_cmd("-m4def")
async def _(conn: Connection, args: list[str]) -> None:
    """Define a macro which i will remember"""
    global loaded
    global command
    command = ""
    while a := input("m4> "):
        if a == "finish":
            break
        command += a
    loaded = True
    
@plugin.register_send_hook
def _(s: str) -> str:
    if s.startswith("-") or not loaded:
        return s
    with Popen(["/bin/m4"], stdin=PIPE, stdout=PIPE, universal_newlines=True) as proc:
        output, _ = proc.communicate(command + s)
        return output


