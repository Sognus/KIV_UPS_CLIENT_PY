from datetime import datetime
import socket
import errno
import time
import threading
import collections


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


class DataReader(threading.Thread):

    def __init__(self, message_parser):
        super().__init__()
        self.message_parser = message_parser

    def run(self):
        print("Data reader started")

        # Start message read
        while self.message_parser.running:
            try:
                data = bytearray(self.message_parser.client.socket.recv(512))
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue
                else:
                    # a "real" error occurred
                    print(e)
                    break
            else:
                if not data:
                    continue
                else:
                    print("{}\n".format(data.decode(encoding="ascii")))
                    self.message_parser.msg += data.decode(encoding="ascii")

        print("Data reader disabled")


class MessageDecoder(threading.Thread):

    def __init__(self, message_parser):
        super().__init__()
        self.message_parser = message_parser
        self.error_count = 0
        self.message_count = 0

        # setup control characters
        self.control_characters = list()
        self.control_characters.append('<')  # Message start
        self.control_characters.append('>')  # Message end
        self.control_characters.append('\\')  # Escape character
        self.control_characters.append(':')  # Value delimiter
        self.control_characters.append(';')  # Pair delimiter
        self.control_characters.append('|')  # Head end

        # Setup ids for routing
        self.game_messages = list()
        self.control_messages = list()
        self.keepalive_messages = list()

        # Control messages
        self.control_messages.append(1000)          # User register
        self.control_messages.append(2000)          # Game create
        self.control_messages.append(2100)          # Game join
        self.control_messages.append(2200)          # Game reconnect
        self.control_messages.append(2300)          # List games

        # Game messages
        self.game_messages.append(2400)             # Game state
        self.game_messages.append(3100)

        # KeepAlive
        self.keepalive_messages.append(1100)        # KeepAlive

    def is_control_character(self, character):
        return character in self.control_characters

    def run(self):
        print("Message decoder started")

        while self.message_parser.running:
            # Wait for message start
            statusWait = self.wait_for_start()

            if statusWait != "ok":
                self.error_count = self.error_count + 1
                continue

            # Throw away start character
            self.message_parser.msg = self.message_parser.msg[1:]

            # Check for id
            statusKeyId = self.read_pair_key("id")

            if statusKeyId != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect pair delimiter
            statusPairDelimiter = self.expect_character(":")

            if statusPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Read number
            id, statusValueId = self.read_pair_value_int()

            if statusValueId != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect end of pair
            statusEndPairDelimiter = self.expect_character(";")

            if statusEndPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Check for rid
            statusKeyRid = self.read_pair_key("rid")

            if statusKeyRid != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect pair delimiter
            statusPairDelimiter = self.expect_character(":")

            if statusPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Read RID number
            rid, statusValueRid = self.read_pair_value_int()

            if statusValueId != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect end of pair
            statusEndPairDelimiter = self.expect_character(";")

            if statusEndPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Check for rid
            statusKeyType = self.read_pair_key("type")

            if statusKeyRid != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect pair delimiter
            statusPairDelimiter = self.expect_character(":")

            if statusPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Read RID number
            type, statusValueType = self.read_pair_value_int()

            if statusValueType != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect end of pair
            statusEndPairDelimiter = self.expect_character(";")

            if statusEndPairDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Expect end of header
            statusEndHeaderDelimiter = self.expect_character("|")

            if statusEndHeaderDelimiter != "ok":
                self.error_count = self.error_count + 1
                continue

            # Create message base
            new_message = Message(id, rid, type)

            # Read message content
            content_read = True
            content_error = False
            while content_read:
                peak_status = self.peak_expect_character(">")

                # We reached end of message
                if peak_status == "ok":
                    break

                # We have something else to read
                key, keyStatus = self.read_pair_key_any()

                if keyStatus != "ok":
                    content_error = True
                    break

                # Expect pair delimiter
                statusPairDelimiter = self.expect_character(":")

                if statusPairDelimiter != "ok":
                    content_error = True
                    break

                # Read pair value
                value, valueStatus = self.read_pair_value_any()

                if valueStatus != "ok":
                    content_error = True
                    break

                # Expect key value end
                statusPairEnd = self.expect_character(";")

                if statusPairEnd != "ok":
                    content_error = True
                    break

                # Message keyvalue was sucessfully parsed add to message
                new_message.add_content(key, value)

            if not content_error:
                # Add message to control messages
                if new_message.type in self.control_messages:
                    self.message_parser.messages.append(new_message)
                # Add message to game messages
                if new_message.type in self.game_messages:
                    self.message_parser.messages_game.append(new_message)
                # Add message to keepalive control
                if new_message.type in self.keepalive_messages:
                    self.message_parser.messages_keepalive.append(new_message)


        print("Message decoder disabled")

    def read_pair_value_any(self):
        buffer = ""
        limit_header = 32
        escape = False

        while True:
            # Check wait limit
            if limit_header < 1:
                return "", "error - wait exceeded"

            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # Read byte from buffer
            character = self.message_parser.msg[0]

            if escape:
                if character == "\\":
                    buffer += character
                    escape = False
                    self.message_parser.msg = self.message_parser.msg[1:]
                    limit_header = limit_header - 1
                else:
                    if self.is_control_character(character):
                        buffer += character
                        escape = False
                        self.message_parser.msg = self.message_parser.msg[1:]
                        limit_header = limit_header - 1
                    else:
                        return "", "error - control byte was expected"
            else:
                if character == "\\":
                    escape = True
                    self.message_parser.msg = self.message_parser.msg[1:]
                    limit_header = limit_header - 1
                else:
                    if character == ";":
                        return buffer, "ok"
                    else:
                        if self.is_control_character(character):
                            return "", "error - unexpected control byte"
                        else:
                            buffer += character
                            self.message_parser.msg = self.message_parser.msg[1:]
                            limit_header = limit_header - 1

    def read_pair_key_any(self):
        buffer = ""
        limit_header = 32
        escape = False

        while True:
            # Check wait limit
            if limit_header < 1:
                return "error - wait exceeded"

            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # Read byte from buffer
            character = self.message_parser.msg[0]

            if escape:
                if character == "\\":
                    buffer += character
                    escape = False
                    self.message_parser.msg = self.message_parser.msg[1:]
                    limit_header = limit_header - 1
                else:
                    if self.is_control_character(character):
                        buffer += character
                        escape = False
                        self.message_parser.msg = self.message_parser.msg[1:]
                        limit_header = limit_header - 1
                    else:
                        return "", "error - control byte was expected"
            else:
                if character == "\\":
                    escape = True
                    self.message_parser.msg = self.message_parser.msg[1:]
                    limit_header = limit_header - 1
                else:
                    if character == ":":
                        return buffer, "ok"
                    else:
                        if self.is_control_character(character):
                            return "", "error - unexpected control byte"
                        else:
                            buffer += character
                            self.message_parser.msg = self.message_parser.msg[1:]
                            limit_header = limit_header - 1

    def peak_expect_character(self, character):
        while True:
            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # Now we have data check
            if self.message_parser.msg[0] == character:
                return "ok"
            else:
                return "error - unexpected character"

    def read_pair_value_int(self):
        buffer = ""
        limit_int = 32

        while True:
            if limit_int < 1:
                return buffer, "error - wait exceeded"

            if len(buffer) > 0 and not buffer.isnumeric():
                return buffer, "error - string is not numeric"

            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # Read byte from buffer
            character = self.message_parser.msg[0]

            # Check if character is control character
            if self.is_control_character(character) and character != ';':
                return buffer, "error - unexpected control character"

            if character == ";":
                if not buffer.isnumeric():
                    return buffer, "error - string is not numeric"
                else:
                    return int(buffer), "ok"
            else:
                buffer += self.message_parser.msg[0]
                self.message_parser.msg = self.message_parser.msg[1:]
                limit_int = limit_int - 1

    def wait_for_start(self):
        limit_start = 512
        start = datetime.now()

        while True:
            if limit_start < 1:
                return "error - wait exceeded"

            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # We now have data - checking for start
            if self.message_parser.msg[0] != "<":
                # We cut data we dont want
                self.message_parser.msg = self.message_parser.msg[1:]
                limit_start = limit_start - 1
            else:
                return "ok"

    def expect_character(self, character):
        while True:
            # If we dont have data we wait for some
            if len(self.message_parser.msg) < 1:
                continue

            # Now we have data check
            if self.message_parser.msg[0] == character:
                self.message_parser.msg = self.message_parser.msg[1:]
                return "ok"
            else:
                return "error - unexpected character"

    def read_pair_key(self, key):
        buffer = ""
        limit_header = 32

        while True:
            # Check wait limit
            if limit_header < 1:
                return "error - wait exceeded"

            start = datetime.now()
            while len(self.message_parser.msg) < 1:
                current = datetime.now()
                check = datetime.now()
                delta = check - start
                if delta.total_seconds() > 2:
                    # Data did not come
                    return "error - no data"

            # Read byte from buffer
            character = self.message_parser.msg[0]

            # Check if character is control character
            if self.is_control_character(character):
                print("unexp cc: " + character)
                return "error - unexpected control character"

            buffer += self.message_parser.msg[0]
            self.message_parser.msg = self.message_parser.msg[1:]

            if buffer == key:
                return "ok"
            else:
                limit_header = limit_header - 1

            # Check if we read more data than we need
            if len(buffer) > len(key):
                return "error - unexpected string"


class MessageParser(threading.Thread):

    def __init__(self, client):
        # Initialize threading constructor
        super().__init__()

        # Client whose messages we are parsing
        self.client = client
        # Send client socket to non blocking to save thread
        self.client.socket.setblocking(0)
        # Parsed messages list - control (FIFO QUEUE)
        self.messages = collections.deque(list())
        # Parsed messages list - game messages (FIFO QUEUE)
        self.messages_game = collections.deque(list())
        # KeepAlive messages list - keep alive messages (FIFO QUEUE)
        self.messages_keepalive = collections.deque(list())
        # Indicate running flag
        self.running = True
        # data buffer
        self.msg = ""

        # Threads
        self.threadDecode = None
        self.threadRead = None

    def stop(self):
        self.running = False

    def run(self):
        self.threadRead = DataReader(self)
        self.threadDecode = MessageDecoder(self)

        self.threadRead.start()
        self.threadDecode.start()

        self.threadRead.join()
        self.threadDecode.join()
