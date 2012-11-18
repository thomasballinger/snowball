import socket
s = socket.socket

from subprocess import Popen

server = Popen(['python', 'server.py', 'localhost'])
client = Popen(['python', 'client.py', 'localhost'])

try:
    raw_input()
except KeyboardInterrupt:
    pass
finally:
    server.kill()
    client.kill()

