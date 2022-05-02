# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

VCC_MAGIC = 0x01328e22

VCC_PORT = 46
VCC_DEFAULT_IP = "124.223.105.230"


class REQ:
    MSG_SEND = 1
    MSG_NEW = 2
    CTL_USRS = 3
    CTL_LOGIN = 4
    CTL_NEWSE = 5
    CTL_SESS = 6
    CTL_JOINS = 7
    CTL_UINFO = 8
    SYS_SCRINC = 9


REQ_SIZE = 512
USERNAME_SIZE = 32
PASSWD_SIZE = 64
MSG_SIZE = REQ_SIZE - 5 * 4 - USERNAME_SIZE

VCC_REQUEST_FORMAT = f"<iiiii{USERNAME_SIZE}s{MSG_SIZE}s"
