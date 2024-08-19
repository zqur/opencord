import socket
import sys
from datetime import datetime
import json
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import threading
import time
import os
import re

"""
        The profile hash is either generated by a third party, an Opencord server, or the Verified Opencord Web server. 

        There might be a profile hash table so a profile can be used with multiple different servers. 
        
                

"""


# This class is used for communication and has all communication information
class Communication:
    def __init__(self, p_hash="default_hash"):
        self.session_id = None  # ID of the chat session
        self.client_version = ""  # Version of the client
        self.server_version = ""  # Version of the server
        self.profile_hash = p_hash  # Hash of the profile
        self.authorization = ""  # Pending auth to begin using the service
        self.sessionToken = ""  # Token for the session
        self.messageNumber = 0  # keeps track of the number of messages sent so far
        self.private_key = None  # Private key (used to decrypt the servers response)
        self.public_key = None  # Public key (used to encrypt the server response)
        self.symmetric_key = None  # symmetric key (sent by the server and used for the rest of the session)
        self.update_packet = False  # If it is an update packet or not
        self.sock = None  # Socket connection

    # Message content, type is the type of message (normal is command or chat, file is a file object)
    def send(self, content, type="normal", size=1024):
        message = {
            "n": self.messageNumber,
            "time": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
            "content": content,
            "token": "NEED TO IMPLEMENT!",
            "type": type,
            "size": size
        }

        self.messageNumber += 1
        return message

    def generateKeys(self):
        key = RSA.generate(2048)
        self.private_key = key.export_key()
        self.public_key = key.export_key().public_key()

    def decrypt(self, message):
        cipher_rsa = PKCS1_OAEP.new(self.private_key)
        # session_key = cipher_rsa.decrypt(enc_session_key)

    # Begin communication with the server 
    def begin(self):
        start_object = {"service": 0, "client_version": self.client_version, "profile": self.profile_hash}
        return start_object


class Data:
    def __init__(self):
        self.server_id = ""  # Server ID
        self.server_name = ""  # Server name
        self.key = ""  # Key
        self.type = ""  # Type of communication (client to client, client to server)
        self.client_version = ""  # Version of the client
        self.client_hash = ""  # Hash of the client

    def get_data(self):
        pass

    def getChat(self, start_date, end_date):
        pass

    # Initiate the communication with the server 
    def start(self):
        pass


def update(timeout=0.5):
    while True:
        size = 1024  # Default size for received messages
        object_size = 0
        buffer = ''
        time.sleep(timeout)
        try:
            data = chat.sock.recv(size)
            try:
                json_data = json.loads(data)
                if 'size' in json_data.keys():
                    object_size = json_data['size']
                    # print(f"Size: {size}")
            except Exception as j:
                # Json error object probably not json type
                # print("Error: not a json object")
                received = str(data, 'utf-8')
                buffer = received

            while object_size > 0:
                data = chat.sock.recv(size)
                received = str(data, 'utf-8')
                buffer += received
                object_size -= size

            # print(f"Received: {received}")

            print("\r" + buffer, end="")
            print("\r" + ">>> ", end="")

        except Exception as e:
            # print(f"Error: {e}")
            pass


if __name__ == "__main__":
    HOST, PORT = "localhost", 9090
    # data = " ".join(sys.argv[1:])

    # sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # sock_udp.sendto(bytes("testing \n", "utf-8"), (HOST, 9091))

    # check if user provided a profile hash
    if len(sys.argv) > 1:
        profile_hash = (sys.argv[1])
        chat = Communication(profile_hash)
    else:
        chat = Communication()
    # Create a socket (SOCK_STREAM means a TCP socket)

    header = """\033[91m
    ·································································
    : _____                                                  __     :
    :/\  __`\                                               /\ \    :
    :\ \ \/\ \  _____      __    ___     ___    ___   _ __  \_\ \   :
    : \ \ \ \ \/\ '__`\  /'__`\/' _ `\  /'___\ / __`\/\`'__\/'_` \  :
    :  \ \ \_\ \ \ \L\ \/\  __//\ \/\ \/\ \__//\ \L\ \ \ \//\ \L\ \ :
    :   \ \_____\ \ ,__/\ \____\ \_\ \_\ \____\ \____/\ \_\\ \___,_\:
    :    \/_____/\ \ \/  \/____/\/_/\/_/\/____/\/___/  \/_/ \/__,_ /:
    :             \ \_\                                             :
    :              \/_/                                             :
    ·································································
    """ + "\u001b[0m" + '\n'

    print(header)

    # This won't open until everything is validated however we are going to do it like this for now

    # Auto update the chat
    update = threading.Thread(target=update, daemon=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        update.start()
        # Connect to server and send data
        data = None
        sock.connect((HOST, PORT))
        hi_packet = json.dumps(chat.begin()).encode('utf-8')  # send in the starter packet
        sock.sendall(hi_packet)  # Say hi to the server and authorize connection
        chat.sock = sock
        while data != "/exit":
            # print("\r>>> ", end="")
            data = input()

            parsed_command = re.sub(r'^\$', '', data)  # Removes the starting slash from the command
            parsed_command = re.sub(r"^\s+", '', parsed_command)  # Removes white spaces from the start of the command
            regex = r"""("[^"]*"|'[^']*'|[\S]+)+"""  # Seperates the command by word and by quoted items
            parsed_command = re.findall(regex, parsed_command)

            # print(f"Parsed command: {parsed_command}")

            match parsed_command[0]:
                case "exit":
                    # Exit the program 
                    break

                case "image":
                    location = parsed_command[1]
                    location = location.strip('\"')  # Remove the quotes
                    print(f"Image Location: {location}")
                    # os.system(location) # Opens the image on your computer in a new window
                    file = open(location, 'rb')
                    sod = os.path.getsize(location)
                    d = chat.send(None, type="file", size=sod)
                    # TO print the file to double check contents
                    # byte = file.read(1)
                    # entire_file = b""
                    # while byte:
                    #     byte = file.read(1)
                    #     entire_file += byte
                    # print(entire_file)
                    # file.close()
                    # file = open(location, 'rb')
                    sock.sendall(
                        json.dumps(d).encode('utf-8'))  # Send prep packet so the server prepares for the actual file
                    sent = sock.sendfile(file)
                    # print(f"File size on disk: {os.path.getsize(location)}")
                    print(f"Sent: {sent} bytes")  # Send
                    file.close()

                    print("\r" + ">>> ", end="")

                case "clear":
                    if sys.platform == "win32":
                        os.system('cls')
                    else:
                        os.system('clear')
                    print("\r" + ">>> ", end="")

                case _:
                    # Default case
                    d = chat.send(data)
                    encoded_data = (json.dumps(d)).encode('utf-8')
                    print(d)

                    sock.sendall(encoded_data)

            # sock.sendall(bytes(d + '\n', 'utf-8'))

            # received = str(sock.recv(1024), 'utf-8')
            # print(received)

            # Receive data from the server and shut down

    # print(f"Sent: {data}")
    # print(f"Received: {received}")
