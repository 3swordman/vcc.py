# type: ignore
# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

# This doesn't work now

from __future__ import annotations

from typing import Any, cast
import math

from Crypto.Cipher import AES

from .constants import *

msg_size = math.floor(MSG_SIZE / 16) * 16

def pad(buf: bytes, size: int) -> bytes:
    assert len(buf + b"\0" * (size - len(buf))) == size
    return buf + b"\0" * (size - len(buf))

class Crypt:
    def __init__(self, key: bytes):
        self.key = key
        
    def reset(self) -> None:
        self.cipher = cast(Any, AES).new(pad(self.key, 32), iv=b"\0" * 16, mode=AES.MODE_CBC)

    def encrypt(self, buf: bytes) -> bytes:
        self.reset()
        print(f"iv: {self.cipher.iv}")
        return cast(bytes, self.cipher.encrypt(pad(buf, msg_size)))

    def decrypt(self, buf: bytes) -> bytes:
        self.reset()
        return cast(bytes, self.cipher.decrypt(buf))

# import pdb
# pdb.set_trace()
