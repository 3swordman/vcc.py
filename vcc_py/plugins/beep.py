# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

import sys
import os
import shlex

from vcc_py.plugin import Plugin
from vcc_py.constants import Request

plugin: Plugin = globals()["plugin"]

@plugin.register_recv_hook
def _(req: Request) -> Request | None:
    print("\a", file=sys.stderr)
    msg = req.msg
    if len(msg) > 10:
        msg = msg[:10] + "..."
    if not sys.platform.startswith("win32"):
        os.system(f"notify-send \"vcc\" \"{shlex.quote(req.usrname)}: {shlex.quote(msg)}\" >/dev/null 2>&1")
    return req


