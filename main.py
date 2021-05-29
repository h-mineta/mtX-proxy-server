#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import ipaddress
import logging
import re
import sys
import threading

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rainbow_logging_handler import RainbowLoggingHandler

from proxy import ProxyServer

parser = argparse.ArgumentParser(description='')
parser.add_argument('--debug',
                    action='store_true',
                    default=False,
                    help='Debug mode(default: False)',)

parser.add_argument('-l', '--listen-address',
                    action='store',
                    nargs='?',
                    default='127.0.0.1',
                    type=str,
                    help='Listen local IPv4 address(default:127.0.0.1)')

parser.add_argument('-p', '--listen-port',
                    action='store',
                    nargs='?',
                    default=443,
                    type=int,
                    help='Listen local port number(default:443)')

parser.add_argument('-P', '--server-port',
                    action='store',
                    nargs='?',
                    default=443,
                    type=int,
                    help='Connect login server port number(default:443)')

parser.add_argument('server_address',
                    action='store',
                    default=None,
                    type=str,
                    help='Connect server IPv4 address')

args = parser.parse_args()

handler = RainbowLoggingHandler(sys.stdout)
if args.debug == True:
    logging.basicConfig(
        level=logging.DEBUG,
        datefmt='%H:%M:%S',
        format='%(asctime)s[%(levelname)-8s] - %(module)-20s:%(funcName)s:L%(lineno)4d : %(message)s',
        handlers=[handler])
else:
    logging.basicConfig(
        level=logging.INFO,
        datefmt='%H:%M:%S',
        format='%(asctime)s[%(levelname)-8s] - %(module)-20s:%(funcName)s:L%(lineno)4d : %(message)s',
        handlers=[handler])
logger = logging.getLogger(__name__)

def terminal_prompt(proxy_server: threading):
    session = PromptSession()

    completer_words = WordCompleter([
        "exit", "quit", "dump_connections"
    ])

    try:
        while True:
            try:
                input_line = session.prompt("> ", auto_suggest=AutoSuggestFromHistory(), completer=completer_words)
            except KeyboardInterrupt:
                logger.warning("KeyboardInterrupt!")
                continue

            matches = re.split(r'\s+', input_line)

            if len(matches) >= 1:
                command = matches[0]
                if command in {"exit", "quit"}:
                    logger.warning("SHUTDOWN!")
                    break

    finally:
        if proxy_server.is_alive() == True:
            proxy_server.join(1)

def main(args: dict):
    try :
        listen_address: ipaddress = ipaddress.ip_address(args.listen_address)
    except ipaddress.AddressValueError as ex:
        raise ex

    try :
        server_address: ipaddress = ipaddress.ip_address(args.server_address)
    except ipaddress.AddressValueError as ex:
        raise ex

    proxy_server = ProxyServer(listen_address, args.listen_port, server_address, args.server_port)
    proxy_server.start()

    terminal_prompt(proxy_server)

if __name__ == "__main__":
    main(args)
