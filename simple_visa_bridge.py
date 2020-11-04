#!/usr/bin/env python3

import socketserver
#import pysiglentsds
from pysiglentsds import *

serial_number="SDS100P2153163"
DEBUG=False

class Handler_TCPServer(socketserver.BaseRequestHandler):
    """
    The TCP Server class for demonstration.

    Note: We need to implement the Handle method to exchange data
    with TCP client.

    """

    def handle(self):        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        print("{} sent: ".format(self.client_address[0]), end="")
        print(self.data)

        result = scope.write(self.data.decode('utf-8'))

        if DEBUG:
            print ("Result: ")
            print(result.decode('utf-8'))
        # just send back ACK for data arrival confirmation
        self.request.sendall(result + b'\x0a')
        #self.request.sendall("ACK from TCP Server".encode())

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999

    scope = pysiglentsds.Sds1102cml(serial_number, setdebug=False)
    # Init the TCP server object, bind it to the localhost on 9999 port
    print ("Start Server on port: " + str(PORT))
    tcp_server = socketserver.TCPServer((HOST, PORT), Handler_TCPServer)

    # Activate the TCP server.
    # To abort the TCP server, press Ctrl-C.
    tcp_server.serve_forever()
