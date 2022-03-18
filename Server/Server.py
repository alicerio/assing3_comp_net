"""
File Transfer Assignment - Assignment 3
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: March 18, 2022

Program will run as following on the terminal:
python3 Server.py
User will have to enter port #
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

    base = 0
    next_seq = 0

    # Have the user choose it perhaps
    window_size = 4

    # File name received from the client
    data = conn.recv(1024).decode()
    print('Asking for file ' + data)

    try:
        # Open file if exists, and send it to the client.
        file = open(data, 'rb')
        data = file.read(1020)
        
        fileExists = True
        print('Sending the file ...')
        while data:
            print(next_seq)
            # Make packet and send it if condition holds
            packet = make(next_seq, data)
            if next_seq < base + window_size:
                send(packet, conn, addr)
                next_seq+=1

            # ACK packet received
            ack_pkt, a = recv(conn)
            print(ack_pkt)
            seq_num, ack_data = extract(ack_pkt)
            if ack_data == b'ACK':
                base = seq_num+1
                if base == next_seq:
                    print
                    # stop time
                else:
                    print
                    # end time
            # if time out:
                # send packets
            data = file.read(1020)
        print('Transfer Complete!')
        print('Connection closed, See you later!')
    except IOError:
        # If file not exists, send an error and exit.
        if not fileExists:
            print('Error: ' + str(sys.exc_info()))

    # Shutdown to tell the client there is no more information to send.
    conn.shutdown(2)
    # conn.close()
