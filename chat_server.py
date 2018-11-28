#!/usr/bin/env python3

import socket
from threading import *
import time
import datetime

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = "127.0.0.1"
port = 65430

serversocket.bind((host, port))

class Message:
    def __init__(self, _message, _nickname):
        self.timestamp = datetime.datetime.now().strftime('[%H:%M:%S]')
        self.message = _message
        self.nickname = _nickname
        self.formatMessage()

    def formatMessage(self):
        self.formatted = self.timestamp
        if self.nickname:
            self.formatted += ' <' + self.nickname + '>'
        self.formatted += ' ' + self.message

class Chatroom:
    def __init__(self):
        self.users = []
        self.messages = []

    def login(self, user, nickname):
        if nickname in self.getNicknames():
            user.sendMessage('Sorry!  That name is taken, please pick another.')
            return False
        else:
            return self.admitUser(user, nickname)

    def admitUser(self, user, nickname):
        user.nickname = nickname

        num_users = len(self.users)
        if num_users:
            welcome_msg = 'Hi ' + user.nickname + '! You are connected with ' + str(num_users) + ' other users: ' + self.printNicknames()
        else:
            welcome_msg = 'Hi ' + user.nickname + '! You are the first one in the room.'
        user.sendMessage(welcome_msg)

        self.messageTheRoom('*' + user.nickname + ' has joined the chat*', None)
        self.users.append(user)
        self.sendRecentMessages(user)

        print ('Logged in! Now there are ' + str(len(self.users)) + ' users in the chat.')

        return True

    def logout(self, user):
        if user in self.users:
            self.users.remove(user)
            self.messageTheRoom('*' + user.nickname + ' has left the chat*', None)
            print ('Logged out! Now there are ' + str(len(self.users)) + ' users in the chat.')

    def messageTheRoom(self, msg, nickname):
        message = Message(msg, nickname)
        self.messages.append(message)
        for u in self.users:
            if u.nickname is not nickname:
                u.sendMessage(message.formatted)
                if '@' + u.nickname in message.message:
                    u.sendMessage('\a')

    def sendRecentMessages(self, user):
        for m in self.messages[-10:]:
            user.sendMessage(m.formatted)

    def getNicknames(self):
        return list(map(lambda x: x.nickname, self.users))

    def printNicknames(self):
        return str(self.getNicknames())

class Messenger(Thread):
    TIMEOUT=0.2

    def __init__(self, _socket):
        Thread.__init__(self)
        self.my_messages = []
        self.socket = _socket
        self.online = True
        self.start()

    def run(self):
        while self.online:
            self.popMessage()
            time.sleep(self.TIMEOUT)

    def sendMessage(self, msg):
        self.my_messages.append(msg)

    def popMessage(self):
        if len(self.my_messages) and self.online:
            msg = self.my_messages.pop(0)
            self.socket.send(msg.encode())


class User(Thread):
    def __init__(self, _socket, _address, _chatroom):
        Thread.__init__(self)
        self.socket = _socket
        self.address = _address
        self.chatroom = _chatroom
        self.logged_in = False
        self.nickname = None
        self.messenger = Messenger(self.socket)
        self.open = True
        self.start()

    def run(self):
        print ('Connected!')
        self.sendMessage('Welcome to chat-app! What is your nickname?')
        while self.open:
            msg = self.readMessage()
            if msg:
                if not self.logged_in:
                    self.logged_in = self.chatroom.login(self, msg)
                else:
                    self.chatroom.messageTheRoom(msg, self.nickname)
        print ('Disconnected!')
        self.messenger.online = False
        self.chatroom.logout(self)

    def readMessage(self):
        data = self.socket.recv(1024)
        if len(data) == 0:
            self.open = False
            return None
        msg = ''
        msg = data.decode()
        return msg

    def sendMessage(self, msg):
        self.messenger.sendMessage(msg)

chatroom = Chatroom()

print ("Waiting for connections...")

serversocket.listen(5)
while True:
    clientsocket, address = serversocket.accept()
    User(clientsocket, address, chatroom)
