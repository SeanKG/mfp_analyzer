from websockets import config, server

# Runs server
print('Starting server on port %s. Waiting for connections...' % config.socket_port)
server.Server().run()



# import socket, threading, time, hashlib, base64

# # TODO: organize this properly in a class / create a server / manager class for connections

# # def resolveKey(key):
# #     concat = bytes(key, "utf-8") + bytes("258EAFA5-E914-47DA-95CA-C5AB0DC85B11", "utf-8")
# #     hashyBoi = hashlib.sha1(concat).digest()
# #     ret = base64.b64encode(hashyBoi)
# #     return ret

# guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

# def parse_headers(data):
#         """
#         Parse client sent headers
#         """
#         headers = {}

#         for l in data.splitlines():
#             parts = l.split(": ", 1)

#             if len(parts) == 2:
#                 headers[parts[0]] = parts[1]

#         return headers

# def resolveKey(key):
#     # return base64.b64encode(hashlib.sha1(key.encode() + guid.encode()).digest())
#     hash = hashlib.sha1(key.encode() + guid.encode())
#     response_key = base64.b64encode(hash.digest()).strip()
#     return response_key.decode('ASCII')

# s = socket.socket()
# s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# s.bind(('', 9876))
# s.listen(1)
# while True:
#     client_connection, client_address = s.accept()
#     #   threading.Thread(target = handle, args = (t,)).start()
#     #   print(repr(s.recv(4096)))
#     print("open")
#     request = client_connection.recv(1024).decode()
#     headers = parse_headers(request)
#     accept = resolveKey(headers['Sec-WebSocket-Key'])
#     print(request)
#     header = '''
# HTTP/1.1 101 Web Socket Protocol Handshake\r
# Upgrade: WebSocket\r
# Connection: Upgrade\r
# WebSocket-Origin: http://localhost:8000\r
# WebSocket-Location: ws://localhost:9876/\r
# Sec-WebSocket-Accept: {0}\r
# WebSocket-Protocol: sample
#     '''.format(accept).strip() + '\r\n\r\n'
#     client_connection.send(header.encode())
#     time.sleep(5)
#     client_connection.send(b'hello')
#     time.sleep(5)
#     client_connection.send(b'world')

# s.close()
