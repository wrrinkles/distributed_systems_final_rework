from enum import Enum
import threading
import argparse
import socket
import os
import zeep

class client:

    # TYPES 
    class RC(Enum):
        OK = 0
        ERROR = 1
        USER_ERROR = 2

    # ATTRIBUTES
    _server = None
    _port = -1
    _running = True
    _username = None
    _system_users = []
    _local_files = []

    # METHODS
    @staticmethod
    def find_free_port(port=1024, max_port=65535):
        """
        Find a free port to bind the server to.
        :param port: The starting port to check.
        :param max_port: The maximum port to check.
        :return: A free port number.
        """
        while port <= max_port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('', port))
                    return port
                except OSError:
                    port += 1
        raise RuntimeError("No free ports available in the specified range.")