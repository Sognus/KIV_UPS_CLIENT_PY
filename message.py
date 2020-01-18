import sys
import socket
import errno
import time
import threading
import collections
import re


class Message:

    def __init__(self, id, rid, type):
        self.id = id
        self.rid = rid
        self.type = type
        self.content = dict()

    def add_content(self, key, val):
        self.content[key] = val

    def get_value(self, key):
        if key in self.content.keys():
            return self.content[key]
        else:
            return None

    def get_key_value_pair(self, key):
        if key in self.content.keys():
            return key, self.content[key]
        else:
            return key, None


class MessageParser(threading.Thread):

    def __init__(self, client):
        # Initialize threading constructor
        super().__init__()

        # Client whose messages we are parsing
        self.client = client
        # Send client socket to non blocking to save thread
        self.client.socket.setblocking(0)
        # Parsed messages list (FIFO QUEUE)
        self.messages = collections.deque(list())
        # Indicate running flag
        self.running = True

    def run(self):
        # Start message parse thread
        while self.running:
            try:
                msg = bytes()
                data = self.client.socket.recv(512)
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
                if not data:
                    continue
                msg += data

                data_text = msg.decode(encoding="ascii")
                # Print data we received
                # print("data received: " + data_text)

                print(data_text)


                # Check if message start with <
                bad_counter = 0
                while len(data_text) > 0 and data_text[0] != '<':
                    data_text = data_text[1:]
                    if bad_counter > 512:
                        continue
                    bad_counter = bad_counter + 1

                # Check message header
                regex_base = r"^\<id:(\d+);rid:(\d+);type:(\d+);\|(.*)>$"
                pattern = re.compile(regex_base)

                # Bad message format
                if not re.match(pattern, data_text):
                    continue

                parsed_data = re.findall(pattern, data_text)

                # More or less parsed data than we need
                if len(parsed_data[0]) != 4:
                    print(len(parsed_data[0]))
                    print(parsed_data[0])
                    continue

                id, rid, type, content = parsed_data[0]

                # Declare message class
                message = Message(id, rid, type)

                for keyval in content.split(";"):
                    if len(keyval) > 0:
                        k, v = keyval.split(":")
                        message.add_content(k, v)

                self.messages.append(message)

        print("Message parser stopped!")
