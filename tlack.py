"""
TODO
Custom port for host and join (optional)
Custom identifier for join (like usernames and color). This prob needs argparse
GUI stuff & prevent double message for sender
"""

import sys
import socket
import threading

# import pytermgui as ptg


# Constants
PORT = 3000
MAX_USERS = 10

class Host:
    def __init__(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        try:
            listener.bind((hostname, PORT))
        except socket.error as e:
            print(str(e))
            sys.exit(1)
        
        print(f'listening on hostname {hostname} port {PORT}')
        listener.listen(MAX_USERS)

        # Array of all connected users
        self.users = []

        while True:
            user, addr = listener.accept()
            print(f'accepted connection from {addr[0]}:{addr[1]}')
            self.users.append(user)

            # Separate thread for this connection
            handler = threading.Thread(target=self.handle_connection, args=(user,))
            handler.start()

    def handle_connection(self, socket):
        while True:
            data = socket.recv(1024)
            if not data:
                break

            # Broadcast the message to all clients
            self.broadcast(data)
            print(data.decode('utf-8'))
        socket.close()

    def broadcast(self, msg):
        for user in self.users:
            user.send(msg)


class Join:
    def __init__(self, hostname: str):
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector.connect((hostname, PORT))

        receiver = threading.Thread(target=self.receive)
        receiver.start()

        sender = threading.Thread(target=self.send)
        sender.start()

    def receive(self):
        while True:
            data = self.connector.recv(1024)
            print(data.decode('utf-8'))

    def send(self):
        while True:
            message = input()
            self.connector.send(message.encode('utf-8'))


def main():
    if len(sys.argv) < 2:
        print('USAGE: tlack COMMAND')
        sys.exit(1)

    if sys.argv[1] == 'host':
        Host()
    elif sys.argv[1] == 'join':
        # If a custom host isn't provided, connect to self
        hostname = socket.gethostname() if len(sys.argv) < 3 else sys.argv[2]
        Join(hostname)
    else:
        print('unknown command. exiting.')
        sys.exit(1)

if __name__ == '__main__':
    main()
