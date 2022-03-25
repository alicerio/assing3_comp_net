"""
File Transfer Assignment - Assignment 2b
CS 5313 - Computer Networks
Last Modified By: Alan Licerio
Last Modified on: March 20, 2022

Program will run as following on the terminal:
python3 Server.py
User will have to enter port # and selected protocol (GBN or SR)
"""

"""
It is needed to terminate the server program at the last packet sent. 
Program is trapped in a deadlock
"""

import sys
import socket
import threading
import packet
import udt
import timer
time = timer.Timer(0.5)
base = 0

# In charge of managing incoming ACKs from client
def receiver(conn):
    global time
    global base
    while True:
        ack_packet, _ = udt.recv(conn)
        ack, _ = packet.extract(ack_packet)
        print('Received ACK #', ack)
        if (ack >= base):
            base = ack + 1
            print('Base = ', base)
            time.stop()


# Function to call for a Go-Back-N pipeline protocol.
# GBN resends entire window size when client/server sequences are inconsistent.
def gbn(conn, addr):
    global time
    global base      # The last acknowledged sequence number
    seq_num = 0      # Current sequence number
    window_size = 4  # *Have the user choose it

    filename_pckt, c = udt.recv(conn)
    ack_seq_num, filename = packet.extract(filename_pckt)
    filename = filename.decode()
    print(filename)

    try:  # Send if file exists
        file = open(filename, 'rb')
        packetsToSend = []  # list of  packets to be sent
        recv_seq_num = 0  # received sequence number
        while True:
            data = file.read(1020)
            if not data:
                break
            packetsToSend.append(packet.make(recv_seq_num, data))
            recv_seq_num = recv_seq_num + 1

        numberOfPackets = len(packetsToSend)  # number of packets that need to be sent
        print("We have to send " + str(numberOfPackets) + " packets")
        next_to_send = 0
        recv_thread = threading.Thread(target=receiver, args=(conn,))
        recv_thread.start()
        while base < numberOfPackets:
            # Send all the packets in the window
            while next_to_send < base + window_size:
                print('Sending packet', next_to_send)
                udt.send(packetsToSend[next_to_send], conn, addr)
                next_to_send = next_to_send + 1

            # Start the timer
            if not time.running():
                print('Start Timer')
                time.start()

            # Wait until a timer goes off or we get an ACK
            while time.running() and not time.timeout():
                time.running()
            if time.timeout():
                print('Timeout')
                time.stop()
                next_to_send = base
        udt.send(packet.make_empty(), conn, addr)
        print("done sending file, have a good day :)")
        file.close()


    except IOError:  # If file does not exist, send error and exit.
        print('Error: ' + str(sys.exc_info()))


# Function to call for a Selective Repeat pipeline protocol.
# SR resends just the packet needed
def sr(conn, addr):
    global time
    global base
    window_size = 24

    filename_pckt, _ = udt.recv(conn)
    _, filename = packet.extract(filename_pckt)
    filename = filename.decode()
    print(filename)

    try:
        file = open(filename, 'rb')
        packetsToSend = []  # list of  packets to be sent
        recv_seq_num = 0  # received sequence number
        while True:
            data = file.read(1020)
            if not data:
                break
            packetsToSend.append(packet.make(recv_seq_num, data))
            recv_seq_num = recv_seq_num + 1
        
        numberOfPackets = len(packetsToSend)  # number of packets that need to be sent
        print("We have to send " + str(numberOfPackets) + " packets")
        next_to_send = 0
        recv_thread = threading.Thread(target=receiver, args=(conn,))
        recv_thread.start()

        # Send one packet at a time if ACK not received before timeout
        # It is just sending one packet ... 
        while base < numberOfPackets:
            print('Sending packet', next_to_send)
            udt.send(packetsToSend[next_to_send], conn, addr)
            next_to_send+=1

            # Timer for each packet sent
            if not time.running():
                print('Start Timer')
                time.start()
            
            while time.running() and not time.timeout():
                time.running()
            if time.timeout():
                time.stop()
                next_to_send = base

        udt.send(packet.make_empty(), conn, addr)
        print("done sending file, have a good day :)")
        file.close()

    except IOError:
        print('Error: ' + str(sys.exc_info()))

# Create new socket and listen to port
serSock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = int(input('Listen at Port #: '))
try:
    serSock.bind(('127.0.0.1', port))                    # Bind to port
except:
    print('Bind failed. Error: ' + str(sys.exc_info()))  # Bind failed
    sys.exit(2)
serSock.listen()                                         # Server ready to listen for connection
print('\nListening for conenction at ' + str(port))


# Select GBN or SR protocol
flag = True
while flag:
    method = input('Select GBN or SR: ').upper()
    if method == 'GBN' or method == 'SR':
        print("Using ", method, "Protocol")
        flag = False


# Listen for connections and send file
while True:
    conn, addr = serSock.accept()       # Accept client connection
    print('Received a connection from:', addr)

    if method == 'GBN':
        print('Sending the file using Go-Back-N')
        thread = threading.Thread(target=gbn, args=(conn, addr))
        thread.start()
    elif method == 'SR':
        print('Sending the file using Selective Repeat')
        thread = threading.Thread(target=sr, args=(conn, addr))
        thread.start()
