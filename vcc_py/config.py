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

class Configs:
    def __init__(self) -> None:
        config_parent_directory_path = Path.home() / ".config"
        config_parent_directory_path.mkdir(0o700, exist_ok=True)

        config_directory_path = config_parent_directory_path / "vcc"
        config_directory_path.mkdir(0o700, exist_ok=True)

        plugins_list_path = config_directory_path / "plugins.txt"
        if not plugins_list_path.exists():
            plugins_list_path.touch(0o700)

        with plugins_list_path.open("r") as file:
            self.plugin_list = [i for i in file.read().split("\n") if i]
        self.plugin_list += ["ban"]
