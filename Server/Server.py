"""
File Transfer Assignment - Assignment 3
CS 5313 - Computer Networks
Last Modified By: Joshua Ramos
Last Modified on: March 20, 2022

Program will run as following on the terminal:
python3 Server.py
User will have to enter port #
"""

"""
*****
GBN SENDS SINGLE MESSAGES, DOES NOT HANDLE LIST PACKETS
MODIFIED UDT.PY TO REFLECT THAT
IT IS PEDNING TO INCORPORATE SLIDING WINDOWS, TIMER, AND LOST PACKET
*****
"""

import sys
import socket
import threading
import packet
import udt
import timer
time = timer.Timer(1)
base = 0

def gbn_receiver(conn):
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
    window_size = 4  # *Have the user choose it perhaps

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
        recv_thread = threading.Thread(target=gbn_receiver, args=(conn,))
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


    while True:
        print(seq_num)
        # Send packet
        pckt = packet.make(seq_num, data)
        if seq_num < base + window_size:
            udt.send(pckt, conn, addr)
            print("Sending #", seq_num)
            seq_num += 1
        # Receive acknowledgement
        ack_pkt, _ = udt.recv(conn)
        ack_seq_num, ack_data = packet.extract(ack_pkt)
        print("Received Ack #", ack_seq_num)
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
    conn.shutdown(2)


# Function to call for a Selective Repeat pipeline protocol.
# GBN resends entire window size when client/server sequences are inconsistent.
def sr(conn, data, addr, file):
    base = 0
    next_seq = 0
    window_size = 4

    while True:
        for _ in range(window_size):
            pckt = packet.make(next_seq, data)
            if next_seq < base + window_size:
                udt.send(pckt, conn, addr)
                next_seq+=1


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
        thread = threading.Thread(target=sr, args=(conn))
        thread.start()
