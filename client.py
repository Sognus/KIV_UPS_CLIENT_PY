import socket
import time


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.playerID = None
        self.messageSent = 0
        self.connect()
        self.keepAlive = time.time()

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def is_connected(self):
        return time.time() - self.keepAlive <= 2

    def refresh_keepalive(self):
        self.keepAlive = time.time()


def request_disconnect(context):
    # Cleanup connection
    print("Cleaning up connection")

    try:
        # Connection failed, disconnect client
        context.parser.running = False
    except:
        pass

    try:
        context.keepalive_thread.running = False
    except:
        pass

    try:
        # Try to send server info to cleanup connection
        disconnect_msg = "<id:{};rid:0;type:20;|playerID:{};>".format(context.client.messageSent,
                                                                      context.client.playerID)
        context.client.messageSent = context.client.messageSent + 1
        context.client.socket.send(bytes(disconnect_msg, "ascii"))
    except:
        # Ignore errors
        pass

    try:
        context.client.socket.close()
    except:
        pass

    context.client = None
    context.parser = None
