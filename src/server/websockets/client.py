import hashlib, base64
from websockets.config import guid, http_host, socket_host, socket_port

class Client:
    """
    A single connection (client) of the program
    """
    def __init__(self, sock, addr, server):
        self.s = sock
        self.addr = addr
        self.server = server

    def run(self):
        """
        Send client connection request
        """
        data = self.s.recv(1024).decode()
        headers = self.parse_headers(data)

        if not 'Sec-WebSocket-Key' in headers:
            raise ValueError('Missing header: Sec-WebSocket-Key')

        accept = base64.b64encode(hashlib.sha1(headers['Sec-WebSocket-Key'].encode() + guid.encode()).digest())

        handshake = ('HTTP/1.1 101 Web Socket Protocol Handshake\r\n'
            'Upgrade: WebSocket\r\n'
            'Connection: Upgrade\r\n'
            'WebSocket-Origin: http://%s\r\n'
            'WebSocket-Location: ws://%s:%s/\r\n'
            'WebSocket-Protocol: sample\r\n'
            'Sec-WebSocket-Accept: %s\r\n\r\n'
            % (http_host, socket_host, socket_port, accept)
        )
        self.s.send(handshake.encode())

        while True:
            data = self.s.recv(1024)

            if not data: continue

            print('Data from', self.addr, ':', data)
            self.onreceive(data)

        self.close()

    def parse_headers(self, data):
        """
        Parse client sent headers
        """
        headers = {}

        for l in data.splitlines():
            parts = l.split(": ", 1)

            if len(parts) == 2:
                headers[parts[0]] = parts[1]

        return headers

    def close(self):
        """
        Close the current connection
        """
        print('Client left: ', self.addr)

        self.server.clients.remove(self)
        self.s.close()

    def send(self, msg):
        """
        Sends a message to the current client
        """
        self.s.send(msg)

    def onreceive(self, data):
        """
        Sends message to all client (server is calling send() method for each connected client)
        """
        self.server.send_to_all(self.addr, data)