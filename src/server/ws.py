import socket, threading, time

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 9876))
s.listen(1)
while True:
    client_connection, client_address = s.accept()
    #   threading.Thread(target = handle, args = (t,)).start()
    #   print(repr(s.recv(4096)))
    print("open")
    request = client_connection.recv(1024).decode()
    print(request)
    header = '''
HTTP/1.1 101 Web Socket Protocol Handshake\r
Upgrade: WebSocket\r
Connection: Upgrade\r
WebSocket-Origin: http://localhost:8000\r
WebSocket-Location: ws://localhost:9876/\r
WebSocket-Protocol: sample
    '''.strip() + '\r\n\r\n'
    client_connection.send(header.encode())
    time.sleep(5)
    client_connection.send('\x00hello\xff')
    time.sleep(5)
    client_connection.send('\x00world\xff')

s.close()
