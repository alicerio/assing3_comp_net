"""
File Transfer Assignment - Assignment 2
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: February 20, 2022

Program will run as following on the terminal:
python Server.py
User will have to enter port #
"""

from socket import *
import sys

# Create new socket
serSock = socket(AF_INET, SOCK_STREAM)
numPort = int(input('Listen at Port #: '))
try:
    # Bind to the given port
    serSock.bind(('127.0.0.1', numPort))
except:
    # Bind failed, causing an error
    print('Bind failed. Error: ' + str(sys.exc_info()))
    sys.exit(2)
# Server ready to listen for connection
serSock.listen(100)

while True:
    print('\nListening for conenction at ' + str(numPort))
    # Accept client connection
    conn, addr = serSock.accept()
    print('Received a connection from:', addr)

    # Boolean flag to determine if the file requested exists on the Server side
    fileExists = False
    # File name received from the client
    data = conn.recv(1024).decode()
    print('Asking for file ' + data)

    try:
        # Open file if exists, and send it to the client.
        file = open(data, 'rb')
        data = file.read(1000)
        fileExists = True
        print('Sending the file ...')
        while data:
            conn.send(data)
            data = file.read(1000)
        print('Transfer Complete!')
        print('Connection closed, See you later!')
    except IOError:
        # If file not exists, send an error and exit.
        if not fileExists:
            print('Error: ' + str(sys.exc_info()))

    # Shutdown to tell the client there is no more information to send.
    conn.shutdown(2)
    # conn.close()
