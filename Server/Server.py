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

# Create new socket and listen to port
serSock = socket(AF_INET, SOCK_STREAM)
numPort = int(input('Listen at Port #: '))
try:
    serSock.bind(('127.0.0.1', numPort))                 # Bind to port
except:
    print('Bind failed. Error: ' + str(sys.exc_info()))  # Bind failed
    sys.exit(2)
serSock.listen(100)                                      # Server ready to listen for connection


# Function to call for a Go-Back-N pipeline protocol.
# GBN resends entire window size when client/server sequences are inconsistent.
def gbn(conn, addr, data, file):
    base = 0         # The last acknowledged sequence number
    seq_num = 0     # Current sequence number
    window_size = 4  # *Have the user choose it perhaps

    while True:
        print(seq_num)
        # Send packet
        packet = make(seq_num, data)
        if seq_num < base + window_size:
            send(packet, conn, addr)
            seq_num += 1
        # Receive acknowledgement
        ack_pkt, _ = recv(conn)
        ack_seq_num, ack_data = extract(ack_pkt)
        if ack_data == b'ACK':
            base = ack_seq_num+1
            if base == seq_num:
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


# Function to call for a Selective Repeat pipeline protocol.
# GBN resends entire window size when client/server sequences are inconsistent.
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


# Select GBN or SR protocol
flag = True
while flag:
    method = input('Select GBN or SR: ').upper()
    if method == 'GBN' or method == 'SR':
        print("Using ", method, "Protocol")
        flag = False
# Listen for connections and send file
while True:
    # Accept client connection
    print('\nListening for conenction at ' + str(numPort))
    conn, addr = serSock.accept()
    print('Received a connection from:', addr)

    # Determine if the file requested exists on the Server side
    fileExists = False                  # True if file exists, false otherwise
    data = conn.recv(1024).decode()     # File name received from the client
    print('Checking for file: ' + data)
    try:                                # Open file if it exists, send it to the client.
        file = open(data, 'rb')
        data = file.read(1020)
        
        fileExists = True
        print('Sending the file ...')
    except IOError:                     # If file does not exist, send error and exit.
        if not fileExists:
            print('Error: ' + str(sys.exc_info()))

    if method == 'GBN':
        gbn(conn, addr, data, file)
    elif method == 'SR':
        sr(conn)

