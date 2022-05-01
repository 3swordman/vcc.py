# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 


from datetime import datetime

import collections

# Colors
BLACK = 0
RED = 1
GREEN = 2
YELLOW = 3
BLUE = 4
MAGENTA = 5
LIGHTBLUE = 6
WHITE = 7
GREY = 60

MODE_DEFAULT = 0
MODE_HIGHLIGHT = 1
MODE_LINE = 4
MODE_BLINK = 5

def fg(color: int) -> int:
    return color + 30

def bg(color: int) -> int:
    return color + 40

Color = collections.namedtuple("Color", ["fg", "bg", "mode"])

usrname_theme = Color(fg=fg(LIGHTBLUE), bg=bg(BLACK), mode=MODE_LINE)
msg_theme = Color(fg=fg(YELLOW), bg=bg(BLACK), mode=MODE_HIGHLIGHT)
time_theme = Color(fg=fg(YELLOW), bg=bg(BLACK), mode=MODE_HIGHLIGHT)


def use_theme(theme: Color, text: str) -> str:
    return f"\033[{theme.mode};{theme.fg};{theme.bg}m{text}\033[0m"

def show_msg(username: str, message: str, newlinefirst=False):
    time = datetime.now()
    str = f"[{use_theme(time_theme, f'{time.hour:02}:{time.minute:02}')}] {use_theme(usrname_theme, username)}@: {use_theme(msg_theme, message)}"
    str = "\r" + str if newlinefirst else str + "\n"
    print(str, end="")

def prompt(username: str):
    print(f"{use_theme(usrname_theme, username)}$: ", end="")