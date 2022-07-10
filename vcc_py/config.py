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
from typing import Any
import yaml

from .readconf import parse

class Configs:
    def __init__(self) -> None:
        readconf_config_path = Path.home() / ".vcc-config"
        yaml_config_path = Path.home() / ".vcc-config.yaml"
        if readconf_config_path.exists():
            config_text = readconf_config_path.read_bytes().decode(errors="ignore")
            self.config: dict[str, Any] = parse(config_text)
        else:
            config_text = yaml_config_path.read_bytes().decode(errors="ignore")
            self.config = yaml.safe_load(config_text)
        plugins: str | list[str] = self.config.get("plugins", "")
        if isinstance(plugins, str):
            self.plugin_list = plugins.split(" ")
        else:
            self.plugin_list = plugins

