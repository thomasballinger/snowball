import os
import socket
s = socket.socket

os.system('python server.py localhost &')
os.system('python client.py localhost')

