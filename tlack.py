"""
TODO
GUI stuff & prevent double message for sender
connect across network instead of single device
disconnect cleanly from host
cmd line args as specifyed in README. prob needs argparse
"""

from blessed import Terminal

import sys
import socket
import threading


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
        self.connector.setblocking(0)
        try:
            self.connector.connect((hostname, port))
        except socket.error as e:
            # 36 is EINPROGRESS, which means the connection is still in progress
            if e.errno != 36:
                print(str(e))
                return

        self.disconnect = False

        print(f'connected to hostname {hostname}.')

        receiver = threading.Thread(target=self.receive)
        receiver.start()
        sender = threading.Thread(target=self.send)
        sender.start()

    def receive(self):
        term = Terminal()
        print(term.home + term.clear)

        with term.cbreak(), term.hidden_cursor():
            while not self.disconnect:
                try:
                    # Maybe this can be blocking!
                    data = self.connector.recv(1024)
                    print(data.decode('utf-8'))
                except socket.error as e:
                    # 35 means there is no data available
                    if e.errno != 35:
                        print(str(e))
                        return

    def send(self):
        message = input()
        while message != 'q' and message != 'quit':
            self.connector.send(message.encode('utf-8'))
            message = input()

        self.disconnect = True


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
