"""
File Transfer Assignment - Assignment 2
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: February 20, 2022

Program will run as following on the terminal:
python Client.py
User will have to enter Server IP and port #
"""

from socket import *
import sys

# Gets IP and Port # input from user
ip = raw_input('Provide server IP: ')
numPort = int(input('Provide Port #: '))

# Creates a new TCP socket
cliSock = socket(AF_INET, SOCK_STREAM)
try:
    # Connects to the Server using the given values
    cliSock.connect((ip, numPort))
    print('You are now connected! Enter your commands now.')
except:
    # Connection to the server was not successful
    print('Connection failed. Error: ' + str(sys.exc_info()))
    sys.exit(2)

RFTcommand = ''
filename = ''

while True:
    # User input to retreive files. 
    RFTcommand = raw_input('RFTCli> ')
    # Split user input to determine which command was used
    split = RFTcommand.split()

    # Flow of the program depending on the command entered
    if (len(split) == 2 and split[0] != 'CLOSE'):
        if(split[0] == "RETR"):
            filename = split[1]
            # Send filename requested to the server
            cliSock.send(filename.encode())
            # Open a new file with the same name
            with open(filename, 'wb') as file:
                while True:
                    # Get packets from the server and write it to the file
                    data = cliSock.recv(1024)
                    if not data:
                        break
                    file.write(data)
            print('Received ' + filename)
    else:
        # Close socket connection
        cliSock.close()
        sys.exit(0)