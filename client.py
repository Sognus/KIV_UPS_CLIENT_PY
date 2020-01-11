import socket


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.playerID = None
        self.connect()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))


def request_disconnect(context):
    # Cleanup connection
    print("Cleaning up connection")

    # Connection failed, disconnect client
    context.parser.running = False

    try:
        # Try to send server info to cleanup connection
        disconnect_msg = "<id:2;rid:2;type:20;|playerID:{};>".format(context.client.playerID)
        context.client.socket.send(bytes(disconnect_msg, "ascii"))
    except:
        # Ignore errors
        pass

    context.client.socket.close()
    context.client = None
    context.parser = None
