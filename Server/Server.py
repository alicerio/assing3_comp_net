"""
File Transfer Assignment - Assignment 3
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: March 19, 2022

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

flag = True
while flag:
    method = input('Select GBN or SR: ')
    if method == 'GBN' or method == 'SR':
        flag = False

try:
    # Bind to the given port
    serSock.bind(('127.0.0.1', numPort))
except:
    # Bind failed, causing an error
    print('Bind failed. Error: ' + str(sys.exc_info()))
    sys.exit(2)
# Server ready to listen for connection
serSock.listen(100)

def gbn(conn, data, addr, file):
    base = 0
    next_seq = 0

    # Have the user choose it perhaps
    window_size = 4

    while True:
        print(next_seq)
        # Make packet and send it if condition holds
        packet = make(next_seq, data)
        if next_seq < base + window_size:
            send(packet, conn, addr)
            next_seq+=1
    # ACK packet received
        ack_pkt, _ = recv(conn)
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
            # send ALL packets
        data = file.read(1020)
        if not data:
            break
    print('Transfer Complete!')
    print('Connection closed, See you later!')

    # Shutdown to tell the client there is no more information to send.
    conn.shutdown(2)
    # conn.close()

def sr(conn, data, addr, file):
    base = 0
    next_seq = 0
    window_size = 4

    while True:
        for _ in range(window_size):
            packet = make(next_seq, data)
            if next_seq < base + window_size:
                send(packet, conn, addr)
                next_seq+=1


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
        data = file.read(1020)
        
        fileExists = True
        print('Sending the file ...')
    except IOError:
        # If file not exists, send an error and exit.
        if not fileExists:
            print('Error: ' + str(sys.exc_info()))

    if method == 'GBN':
        gbn(conn, data, addr, file)
    elif method == 'SR':
        sr(conn)

