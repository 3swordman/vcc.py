# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from pathlib import Path
from typing import Awaitable, Callable, TypeAlias
import importlib

from .sock import Connection
from .constants import *

send_hook_type: TypeAlias = Callable[[str], str | None]
recv_hook_type: TypeAlias = Callable[[Request], Request | None]
cmd_type: TypeAlias = Callable[[Connection, list[str]], Awaitable[None]]

class Plugin:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn
        self._send_hooks: list[send_hook_type] = []
        self._recv_hooks: list[recv_hook_type] = []
        self.cmds: dict[str, cmd_type] = {}

    def get_send_hooks(self) -> list[send_hook_type]:
        return self._send_hooks

    def register_send_hook(self, func: send_hook_type) -> send_hook_type:
        self._send_hooks.append(func)
        return func

    def get_recv_hooks(self) -> list[recv_hook_type]:
        return self._recv_hooks

    def register_recv_hook(self, func: recv_hook_type) -> recv_hook_type:
        self._recv_hooks.append(func)
        return func

    def register_cmd(self, name: str) -> Callable[[cmd_type], cmd_type]:
        def func(cmd_func: cmd_type) -> cmd_type:
            self.cmds[name] = cmd_func
            return cmd_func
        return func

class Plugins:
    def __init__(self, conn: Connection) -> None:
        self.path = Path(__file__).absolute().parent / "plugins"
        self.module_names = [i.with_suffix("").name for i in self.path.iterdir() if i.is_file() and i.name != "__init__.py"]
        self.modules = [importlib.import_module(f".plugins.{name}", __package__) for name in self.module_names]
        self.init_funcs: list[Callable[[Plugin], None]] = [module.init for module in self.modules]
        self.plugs: list[Plugin] = []
        for init in self.init_funcs:
            plug = Plugin(conn)
            init(plug)
            self.plugs.append(plug)

    def send_msg(self, msg_: str) -> str | None:
        msg: str | None = msg_
        for i in self.plugs:
            for j in i.get_send_hooks():
                if msg is None:
                    break
                msg = j(msg)
        return msg

    def recv_msg(self, msg_: Request) -> Request | None:
        msg: Request | None = msg_
        for i in self.plugs:
            for j in i.get_recv_hooks():
                if msg is None:
                    break
                msg = j(msg)
        return msg

    def get_commands(self) -> dict[str, cmd_type]:
        cmds: dict[str, cmd_type] = {}
        for i in self.plugs:
            cmds.update(i.cmds)
        return cmds