# This file is part of vcc.py.

# vcc.py is free software: you can redistribute it and/or modify it under the terms of the GNU General 
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at 
# your option) any later version.

# vcc.py is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the 
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public 
# License for more details.

# You should have received a copy of the GNU General Public License along with vcc.py. If not, see 
# <https://www.gnu.org/licenses/>. 

import _thread as thread

import sys
from getpass import getpass
import argparse
import logging
import time
from datetime import datetime

from sock import Connection
from constants import *
import pretty

def parse_args():
    parser = argparse.ArgumentParser(description="Talk with others using %(prog)s :)")
    parser.add_argument("-p", "--port", type=int, metavar="port", default=VCC_PORT, help="specified the port the server use (defualt: 46)")
    parser.add_argument("-u", "--user", type=str, metavar="username", help="the username you want to use")
    parser.add_argument(dest="ip", metavar="ip", nargs="?", default=VCC_DEFAULT_IP, help="the ip address of the server")
    return parser.parse_args()

def recv_loop(conn: Connection):
    while True:
        type, uid, session, flags, usrname, msg = conn.recv()
        time = datetime.now()
        pretty.show_msg(usrname, msg, newlinefirst=True)
        pretty.prompt(curr_usrname)

def request_recv_loop(conn: Connection):
    while True:
        time.sleep(1)
        conn.send(type=REQ_MSG_NEW)

def input_send_loop(conn: Connection):
    while True:
        time = datetime.now()
        pretty.prompt(curr_usrname)
        msg = input("")
        conn.send(
            type=REQ_MSG_SEND,
            usrname=curr_usrname,
            msg=msg
        )
        pretty.show_msg(curr_usrname, msg)

def main():
    connection.send(
        type=REQ_CTL_LOGIN,
        usrname=curr_usrname,
        msg=password
    )
    type, uid, *_ = connection.recv()
    if type != REQ_CTL_LOGIN:
        raise Exception("Invalid response received")
    if not uid:
        raise Exception("login failed: wrong password or user doesn't exists")
    print("ready.")
    thread.start_new_thread(recv_loop, (connection, ))
    thread.start_new_thread(request_recv_loop, (connection, ))
    input_send_loop(connection)
    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
    args = parse_args()
    connection = Connection(args.ip, args.port)
    curr_usrname: str = args.user if args.user else input("login as: ")
    password = getpass("password: ")
    try:
        main()
    except Exception as e:
        logging.error(e)
        sys.exit(1)