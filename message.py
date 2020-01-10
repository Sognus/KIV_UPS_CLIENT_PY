import sys
import socket
import errno
import time
import threading


class MessageParser(threading.Thread):

    def __init__(self, client):
        # Initialize threading constructor
        super().__init__()

        self.client = client
        # Send client socket to non blocking to save thread
        self.client.socket.setblocking(0)

    def run(self):
        # Start message parse thread
        while True:
            try:
                msg = self.client.socket.recv(256)
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    time.sleep(0.3)
                    continue
                else:
                    # a "real" error occurred
                    print(e)
                    break
            else:
                print("data received: " + str(msg))
                # got a message, do something :)
