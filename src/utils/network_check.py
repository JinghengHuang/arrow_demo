"""
Utility functions to check if a network port is open.
"""
import socket
from contextlib import closing

def check_socket(host, port):
    """Check if a port is open.

    Args:
        host (string): host
        port (int): port

    Returns:
        Boolean: if the port is open
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return True
        else:
            return False
