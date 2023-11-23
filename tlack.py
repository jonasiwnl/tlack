"""
TODO
GUI stuff & prevent double message for sender
connect across network instead of single device
Custom identifier for join (like usernames and color). This prob needs argparse
Make it possible to pass port like server:port as well as server port
"""

import sys
import socket
import threading

# import pytermgui as ptg


# Constants
DEFAULT_PORT = 3000
MAX_USERS = 10

class Host:
    def __init__(self, port: int):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()

        # Attempt to bind to port, if it fails, try the next port
        for _ in range(5):
            try:
                listener.bind((hostname, port))
                # Reuse address for frequent stops/starts
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                break
            except socket.error as e:
                if e.errno == socket.errno.EADDRINUSE:
                    print(f'port {port} is already in use. attempting to use port {port + 1}.')
                    port += 1
                    continue

                print(str(e))
                return
        
        print(f'listening on hostname {hostname} port {port}')
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
    def __init__(self, hostname: str, port: int):
        self.connector = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connector.connect((hostname, port))
        except socket.error as e:
            print(str(e))
            return

        print(f'connected to hostname {hostname}.')

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
        print('USAGE: tlack [host | join] [ARGS]')
        sys.exit(1)

    if sys.argv[1] == 'host':
        # tlack host [port]
        port = DEFAULT_PORT if len(sys.argv) < 3 else int(sys.argv[2])
        Host(port)
    elif sys.argv[1] == 'join':
        # tlack join [hostname] [port]
        hostname = socket.gethostname() if len(sys.argv) < 3 else sys.argv[2]
        port = DEFAULT_PORT if len(sys.argv) < 4 else int(sys.argv[3])
        Join(hostname, port)
    else:
        print('unknown command. exiting.')
        sys.exit(1)

if __name__ == '__main__':
    main()
