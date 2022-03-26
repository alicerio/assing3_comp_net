"""
File Transfer Assignment - Assignment 3
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: March 20, 2022

Program will run as following on the terminal:
python3 Client.py
User will have to enter Server IP port # and selected protocol.
Protocol has to be the same as the server.
"""


import sys
import socket
import packet
import udt

# Creates a new socket
cliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(input('Provide Port #: '))
addr = ('127.0.0.1', port)

# Select GBN or SR protocol
flag = True
while flag:
    method = input('Select GBN or SR: ').upper()
    if method == 'GBN' or method == 'SR':
        print("Using ", method, "Protocol")
        flag = False

try:
    cliSock.connect(('127.0.0.1', port))
    print('You are now connected! Enter your commands now.')
except:
    print('Connection failed. Error: ' + str(sys.exc_info()))
    sys.exit(2)
    

RFTcommand = ''
filename = ''
next_seq = 0
buffer = []
while True:
    # User input to retreive files.
    RFTcommand = input('RFTCli> ')
    # Split user input to determine which command was used
    split = RFTcommand.split()

    # Flow of the program depending on the command entered
    if (len(split) == 2 and split[0] == "RETR"):
        filename = split[1]
        # Send filename request to the server
        first_pckt = packet.make(0, filename.encode())
        udt.send(first_pckt, cliSock, addr)

        # Open a new file with the same name
        with open(filename, 'wb') as file:
            expected_seq_num = 0
            while True:
                # Get packets from the server and write it to the file
                pckt, s = udt.recv(cliSock)
                if pckt == b'':  # Break loop if no more data
                    print("Done Receiving")
                    break
                seq_num, data = packet.extract(pckt)
                print("Received packet #", seq_num)
                if seq_num == expected_seq_num:
                    if method == 'SR':
                        # Insert packet to buffer if using SR protocol
                        buffer.insert(seq_num, data)
                    else :
                        file.write(data)

                    ack_pckt = packet.make(expected_seq_num, b'')  # Create ACK message
                    udt.send(ack_pckt, cliSock, addr)
                    expected_seq_num += 1
                else:
                    print('Re-Sending ACK', expected_seq_num - 1)
                    ack_pckt = packet.make(expected_seq_num - 1, b'')
                    udt.send(ack_pckt, cliSock, addr)
            if method == 'SR':
                for data in buffer:
                    file.write(data)
        file.close()
        cliSock.close()
        print('Received ' + filename)
    else:
        # Close socket connection
        cliSock.close()
        sys.exit(0)