#!/usr/bin/env python3

import socket
from threading import *

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 65430

socket.connect((host,port))

class ClientRead(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.sock = socket
        self.start()

    def run(self):
        while True:
            self.readMessage()

    def readMessage(self):
        data = ''
        data = self.sock.recv(1024).decode()
        if data:
            if data == '\a':
                print ("!!BELL!!" + data)
            else: print (data)

class ClientWrite(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.sock = socket
        self.start()

    def run(self):
        while True:
            self.sendMessage()

    def sendMessage(self):
        msg = input()
        self.sock.send(msg.encode())

clientRead = ClientRead(socket)
clientWrite = ClientWrite(socket)
