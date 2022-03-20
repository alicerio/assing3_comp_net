"""
File Transfer Assignment - Assignment 3
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: March 18, 2022

Program will run as following on the terminal:
python3 Client.py
User will have to enter Server IP and port #
"""

"""
*****
ONLY GBN WORKING ASSUMING NO PACKET IS LOST.
MODIFIED UDT.PY TO REFLECT THAT
IT IS PEDNING TO INCORPORATE THE TIMER AND LOST PACKET
PROB
*****
"""

from socket import *
import sys
from packet import *
from udt import *

# Get IP and Port # from user input
# ip = raw_input('Provide server IP: ')
numPort = int(input('Provide Port #: '))
# Creates a new TCP socket
cliSock = socket(AF_INET, SOCK_STREAM)
try:
    # Connects to the Server using the given values
    cliSock.connect(('127.0.0.1', numPort))
    print('You are now connected! Enter your commands now.')
except:
    # Connection to the server was not successful
    print('Connection failed. Error: ' + str(sys.exc_info()))
    sys.exit(2)


RFTcommand = ''
filename = ''
next_seq = 0

while True:
    # User input to retreive files. 
    RFTcommand = input('RFTCli> ')
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
                    packet, addr = recv(cliSock)
                    seq_num, data = extract(packet)

                    # Temp solution to get address
                    addr = tuple(('127.0.0.1', numPort))
                    if not data:
                        break
                    else:
                        file.write(data)
                        # Create ACK message
                        ack_data = b'ACK'
                        ack_pkt = ''
                        # Create ACK packet
                        if seq_num == next_seq:
                            ack_pkt = make(next_seq, ack_data)
                            next_seq+=1
                        else:
                            ack_pkt = make(next_seq-1, ack_data)
                        send(ack_pkt, cliSock, addr)

            print('Received ' + filename)
    else:
        # Close socket connection
        cliSock.close()
        sys.exit(0)