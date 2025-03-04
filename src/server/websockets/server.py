import socket, threading
from websockets.config import socket_host, socket_port
from websockets.client import Client

"""
Originally taken from: https://github.com/eko/python-websocket/blob/master/websocket/wsserver.py
Adapted for python3
"""

class Server:
    """
    Initializes server that will store client connections
    """
    def __init__(self):
        self.clients = []
        self.threads = []

    def run(self):
        """
        Starts the server
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((socket_host, socket_port))
        s.listen(5)

        try:
            while True:
                conn, addr = s.accept()

                newClient = Client(conn, addr, self)

                t = threading.Thread(target=newClient.run)
                t.start()

                self.threads.append(t)
                self.clients.append(newClient)

                print('New client connected', addr)
        except KeyboardInterrupt:
            [client.close() for client in self.clients]
            [thread._Thread__stop() for thread in self.threads]
            s.close()

    def remove(self, client):
        """
        Removes a client
        """
        self.clients.remove(client)

    def send_to_all(self, from_addr, data):
        """
        Sends a message to all clients
        """
        for client in self.clients:
            if client.addr == from_addr: continue
            client.send(data)