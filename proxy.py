import ipaddress
import logging
import select
import socket
import socketserver
import ssl
import threading

logger = logging.getLogger(__name__)

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    remote_address: ipaddress.IPv4Address = None
    remote_port: int = 443

    connection = None
    buffer = b""

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        response = bytes(data, 'utf_8')
        #self.request.sendall(response)
        print(data)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address: bool = True

class ProxyServer(threading.Thread):
    listen_address: ipaddress= None
    listen_port: int = 443
    remote_address: ipaddress= None
    remote_port: int = 443

    ssl_server: ThreadedTCPServer = None

    def __init__(self, listen_address: ipaddress, listen_port: int, remote_address: ipaddress, remote_port: int):
        super().__init__()
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.remote_address = remote_address
        self.remote_port = remote_port

    def run(self):
        super().run()

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile="./pem/fullchain.pem", keyfile="./pem/privkey.pem")
        ssl_context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        self.ssl_server = ThreadedTCPServer((str(self.listen_address), self.listen_port), ThreadedTCPRequestHandler)

        self.ssl_server.socket = ssl_context.wrap_socket(self.ssl_server.socket, server_side=True)
        self.ssl_server.serve_forever()
        self.ssl_server.server_close()

    def match_maker(self, poll: select, client_fileno: int):
        # Remote side
        ssl_context = ssl.create_default_context()
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.check_hostname = False
        ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

        remote_socket = socket.create_connection((str(self.remote_address), self.remote_port))

    def join(self, timeout: int=None):
        super().join(timeout)
        try:
            self.ssl_server.shutdown()
        except:
            pass
