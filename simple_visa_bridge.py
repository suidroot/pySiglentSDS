import socketserver
import visa

serial_number="SDS100P2153163"

class Sds1102cml:


    def __init__(self, serial_number):
        resource_string = "USB0::0xF4EC::0xEE3A::" + serial_number + "::0::INSTR"

        self.resources = visa.ResourceManager('@py')
        self.device = resources.open_resource(resource_string)

    def sendcommand(self, command):
        
        self.device.write(command)
        response = self.device.read_raw()

        return response


class Handler_TCPServer(socketserver.BaseRequestHandler):
    """
    The TCP Server class for demonstration.

    Note: We need to implement the Handle method to exchange data
    with TCP client.

    """

    def handle(self):
        # self.request - TCP socket connected to the client
        self.data = self.request.recv(1024).strip()

        scope.sendcommand(self.data)

        print("{} sent:".format(self.client_address[0]))
        print(self.data)
        # just send back ACK for data arrival confirmation
        self.request.sendall("ACK from TCP Server".encode())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    scope = Sds1102cml(serial_number)
    # Init the TCP server object, bind it to the localhost on 9999 port
    tcp_server = socketserver.TCPServer((HOST, PORT), Handler_TCPServer)

    # Activate the TCP server.
    # To abort the TCP server, press Ctrl-C.
    tcp_server.serve_forever()