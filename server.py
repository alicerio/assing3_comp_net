#! /usr//bin/env python3
# A file transfer client

import sys
from socket import *
from select import select
import os.path
import time

# Addresses and Ports
if len(sys.argv) == 1:              # If port not specified, any addr, port 50,000
    fileTransferPort = ("", 50000)
elif len(sys.argv) > 2:             # If more parameters were selected
    print('Usage: "python broken_server.py [portNum]"\n\t[portNum] is the port number for the server. Valid range: 1024-65535')
    sys.exit(2)
else:                               # Check for valid parameter
    try:
        fileTransferPort = ("", int(sys.argv[1]))
    except ValueError:
        print("Invalid port!")
        sys.exit(2)

# File info
f = ""
filename = ""
byte = b''
fileSize = 0
seqNumLength = 1
sequenceNum = 0


# Run this function when receiving a message
def recvMsg(sock):
    global f, filename, byte, fileSize, seqNumLength, sequenceNum
    # message: [Sequence Number][Message]
    message, clientAddrPort = sock.recvfrom(2048)
    if message[0:4] == b'RETR':                              # message is a new file request
        filename = message[4:].decode()
        try:                                                 # If file exists, initialize file transfer
            f = open(filename, "rb")
            fileSize = os.path.getsize(filename)
            while 256 ** seqNumLength < fileSize:
                seqNumLength += 1
            sequenceNum = 0
            sendFile(sock, clientAddrPort)
        except IOError:                                      # If file does not exists
            print('File %s is not in directory' % filename)
            sequenceNum = -1
            sendFile(sock, clientAddrPort)
    else:                                                    # message is not a new file request
        ackSeqNum = message[0:seqNumLength]
        message = message[seqNumLength:]
        print('From %s: Sequence: %d, Message: "%s"' % ((clientAddrPort), int.from_bytes(ackSeqNum, "big"), message.decode()))
        if int.from_bytes(ackSeqNum, "big") == sequenceNum:  # Send next message
            if len(byte) == 0 and int.from_bytes(ackSeqNum, "big") != 0:  # If length of byte == 0 here, that means that the END message was acknowledged
                print("TRANSMISSION SUCCESS!")
            else:
                byte = f.read(1000)
                sequenceNum += 1
                sendFile(sock, clientAddrPort)
        elif int.from_bytes(ackSeqNum, "big") < sequenceNum:  # Error, resend previous message
            print("Ack was for an older message, resending current message.")
            sequenceNum = int.from_bytes(ackSeqNum, "big") + 1
            sendFile(sock, clientAddrPort)
        else:
            print("There was an unknown error.")


# Send file content
def sendFile(sock, clientAddrPort):
    try:
        if sequenceNum == -1:
            # message = [File name length][Filename][Sequence # length][Sequence Error #][Error Message]
            message = len(filename).to_bytes(1, "big") + bytearray(filename, 'utf-8') + \
                      seqNumLength.to_bytes(1, "big") + sequenceNum.to_bytes(seqNumLength, "big") + bytearray("File not found", 'utf-8')
        elif sequenceNum == 0:
            # message = [File name length][Filename][Sequence # length][Sequence #0][File size]
            message = len(filename).to_bytes(1, "big") + bytearray(filename, 'utf-8') + \
                      seqNumLength.to_bytes(1, "big") + sequenceNum.to_bytes(seqNumLength, "big") + \
                      fileSize.to_bytes(seqNumLength, "big")
        else:
            # message = [File name length][Filename][Sequence # length][Sequence #][File content]
            message = len(filename).to_bytes(1, "big") + bytearray(filename, 'utf-8') + \
                      seqNumLength.to_bytes(1, "big") + sequenceNum.to_bytes(seqNumLength, "big") + byte
        sock.sendto(message, clientAddrPort)
        print("\t\t\t\t\t\t\tSent Msg: #%d" % sequenceNum)
    except IOError:
        print('Error sending %s' % filename)


# Listening to fileTransferPort
fileTransferServerSocket = socket(AF_INET, SOCK_DGRAM)
fileTransferServerSocket.bind(fileTransferPort)
fileTransferServerSocket.setblocking(False)

# Map socket to function to call when socket is:
readSockFunc = {}  # ready for reading
writeSockFunc = {}  # ready for writing
errorSockFunc = {}  # broken

# function to call when fileTransferSocket is ready for reading acknowledgement
readSockFunc[fileTransferServerSocket] = recvMsg

print("SERVER RUNNING\nListening to port: %s" % repr(fileTransferPort))
print("*******************************\nReady to receive")
# Repeatetly listen for connections
timeout = 5  # Seconds to wait before reattempting
while 1:
    readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                  list(writeSockFunc.keys()),
                                                  list(errorSockFunc.keys()),
                                                  timeout)

    if not readRdySet and not writeRdySet and not errorRdySet:
        print("timeout: no events")
    for sock in readRdySet:
        readSockFunc[sock](sock)