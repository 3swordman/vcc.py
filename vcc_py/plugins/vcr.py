# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from typing import Generator
import os

from vcc_py.constants import *
from vcc_py.plugin import Plugin

# This is not encourged to use, you had better write a plugin instead

plugin: Plugin = globals()["plugin"]

config = plugin.configs.config

sid = config["vcr_listen_sid"]

@plugin.register_init_func
def _(data: MyData) -> Generator[None, None, None]:
    yield
    os.unsetenv("VCR_TYPE")
    os.unsetenv("VCR_USER")
    os.unsetenv("VCR_MSG")
    os.unsetenv("VCR_SID")

@plugin.register_recv_hook
def _(req: Request) -> Request:
    if req.session != sid:
        return req
    os.putenv("VCR_TYPE", str(req.type))
    os.putenv("VCR_USER", req.usrname)
    os.putenv("VCR_MSG", req.msg)
    os.putenv("VCR_SID", str(sid))
    os.system(f"{config['vcr_executable']}")
    return req
