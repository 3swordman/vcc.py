# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

from __future__ import annotations

from types import TracebackType
from typing import Awaitable, Callable, Generator, TypeAlias
import importlib

from .sock import Connection
from .constants import *
from .config import Configs
from .plugins import *

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
        self.configs = Configs()
        self.configs.plugin_list
        self.module_names = self.configs.plugin_list
        try:
            self.modules = [importlib.import_module(f".plugins.{name}", __package__) for name in self.module_names]
        except ImportError:
            # Find some module that cannot be imported
            self.init_funcs: list[Callable[[Plugin], Generator[None, None, None]] | Callable[[Plugin], None]] = []
            self.init_results: list[Generator[None, None, None]] = []
            self.plugs: list[Plugin] = []
        self.init_funcs = [module.init for module in self.modules]
        self.init_results = []
        self.plugs = []
        self.connection = conn
        for init in self.init_funcs:
            plug = Plugin(conn)
            result = init(plug)
            if result is not None:
                self.init_results.append(result)
                next(self.init_results[-1])
            
            self.plugs.append(plug)

    def add_plugin(self, name: str) -> None:
        try:
            self.modules.append(importlib.import_module(f".plugins.{name}", __package__))
        except ImportError:
            print("Cannot find the plugin")
            return None
        self.init_funcs.append(self.modules[-1].init)
        plug = Plugin(self.connection)
        result = self.init_funcs[-1](plug)
        if result is not None:
            self.init_results.append(result)
            next(self.init_results[-1])

        self.plugs.append(plug)

    def __enter__(self) -> Plugins:
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        for i in self.init_results:
            try:
                next(i)
            except StopIteration:
                pass

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
