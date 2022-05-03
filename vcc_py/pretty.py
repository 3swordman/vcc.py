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

def to_fg(color: int) -> int:
    return color + 30

def to_bg(color: int) -> int:
    return color + 40

class Color:
    """the color theme"""
    __slots__ = ("fg", "bg", "mode")
    def __init__(self, *, fg: int, bg: int, mode: int):
        self.fg = to_fg(fg)
        self.bg = to_bg(bg)
        self.mode = mode

usrname_theme = Color(fg=LIGHTBLUE, bg=BLACK, mode=MODE_LINE)
msg_theme = Color(fg=YELLOW, bg=BLACK, mode=MODE_HIGHLIGHT)
time_theme = Color(fg=YELLOW, bg=BLACK, mode=MODE_HIGHLIGHT)
cqd_theme = Color(fg=BLACK, bg=RED, mode=MODE_BLINK)
session_theme = Color(fg=RED, bg=BLACK, mode=MODE_HIGHLIGHT)
level_theme = Color(fg=YELLOW, bg=BLACK, mode=MODE_LINE)

def use_theme(theme: Color, text: str) -> str:
    """change some text to the color"""
    return f"\033[{theme.mode};{theme.fg};{theme.bg}m{text}\033[0m"

def show_msg(username: str, message: str, sess: int, newlinefirst: bool=False) -> None:
    """display someone's message"""
    time = datetime.now()
    str = f"[{use_theme(time_theme, f'{time.hour:02}:{time.minute:02}')}] {session(sess)} {use_theme(usrname_theme, username)}@: {use_theme(msg_theme, message)}"
    str = "\r" + str if newlinefirst else str + "\n"
    print(str, end="")

def session(sess: int) -> str:
    """display the session"""
    return use_theme(session_theme, f'#{sess:03}')

def cqd(username: str) -> None:
    """show the cqd"""
    print(f"\n{use_theme(cqd_theme, 'CQD')} {username} send CQD. ", end="")

def level(level: int) -> str:
    """display the level"""
    return use_theme(level_theme, f"lvl{level:02}")

def prompt(username: str, sess: int, lvl: int) -> None:
    """display the prompt"""
    print(f"{level(lvl)} {session(sess)} {use_theme(usrname_theme, username)}$: ", end="")

