from enum import Enum
import threading
import argparse
import socket
import os
import zeep

class client:

    # ========== TYPES ========== 
    class RC(Enum):
        OK = 0
        ERROR = 1
        USER_ERROR = 2

    #  ========== ATTRIBUTES ==========
    _server = None
    _port = -1
    _running = True
    _username = None
    _system_users = []
    _local_files = []

    # ========== METHODS ==========
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

    @staticmethod
    def listen_thread(ServerSocket):
        """
        Thread function to listen for incoming connections from other users.
        :param ServerSocket: The server socket to listen on.
        """
        # Timeout to avoid blocking indefinitely
        ServerSocket.settimeout(1.0)

        # Listen for incoming connections; backlog queue set to 5 for testing purposes (might change)
        ServerSocket.listen(5)

        # Set running to True to indicate that the client is running
        client._running = True

        # Loop to accept incoming connections and handle different types of requests
        while client._running:
            try:
                # Accept incoming connection
                conn, user_addr = ServerSocket.accept()

                # Wait for the user to send a request
                service = ""
                while True:
                    msg = conn.recv(1)

                    if msg == b'\0':
                        break

                    service += msg.decode()

                # Confirm the service requested by the user
                if service == "GET_FILE":
                    # Receive the filename requested by the user
                    filename = ""

                    while True:
                        msg = conn.recv(1)

                        if msg == b'\0':
                            break

                        filename += msg.decode()

                    # Search for requested file in local files
                    file_path = ".local_files/" + filename

                    if os.path.exists(file_path):
                        res = 0     # file found

                    else:
                        res = 1     # file not found

                else:
                    res = 2    # Error: invalid service requested

                # Return the result of the request to the user
                conn.sendall(str(res).encode())

                # Send content of the file if it was found
                if res == 0:
                    with open(file_path, 'r') as file:      # Currently considering only text files; might change
                        file_content = file.read()

                    # Add a null terminator to the end of the file content
                    file_content += '\0'

                    # Send the file content to the user
                    conn.sendall(file_content.encode())

            except socket.timeout:
                # Timeout, pass and check status of client._running
                pass

            finally:
                # Close the connection to the user if one was established
                if 'conn' in locals():
                    conn.close()

        # Close the server socket when the client is no longer running
        ServerSocket.close()