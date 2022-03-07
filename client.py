#! /usr/bin/env python3
# A file transfer server

import sys
from socket import *
from select import select
import os.path

# Addresses and Ports
if len(sys.argv) == 1:  # If port not specified, localhost, port 50,000
    serverAddr = ('localhost', 50000)
elif len(sys.argv) != 3:  # If not the correct parameters
    print('Usage: "python client.py [serverAddr] [portNum]"'
          '\n\t[serverAddr] is the server address. Suggested address: "localhost" or "127.0.0.1"'
          '\n\t[portNum] is the port number for the server. Valid range: 1024-65535')
    sys.exit(2)
else:
    try:
        serverAddr = (sys.argv[1], int(sys.argv[2]))
    except ValueError:
        print("Invalid port!\nValid range: 1024-65535")
        sys.exit(2)

lastSequenceNum = -1


# Run this function when receiving a message
def recvMsg():
    global lastSequenceNum
    # message: [File name length][Filename][Sequence # length][Sequence #0][File Length/File content]
    message, serverAddrPort = clientSocket.recvfrom(2048)
    # print("Message from %s: rec'd: " % (repr(clientAddrPort)), message)
    filename = message[1: message[0] + 1]
    message = message[message[0] + 1:]
    seqByteLen = message[0]
    sequenceNum = message[1: seqByteLen+1]
    message = message[seqByteLen + 1:]
    if len(message) > 0:                                # Check if not EOF
        wFileContent(serverAddrPort, filename, seqByteLen, sequenceNum, message)
    else:                                               # EOF
        print("Reached EOF of %s." % filename.decode())
        ackMsg = "Rec'd EOF of %s." % filename.decode()
        clientSocket.sendto(sequenceNum + bytearray(ackMsg, 'utf-8'), serverAddrPort)  # message: [Sequence Number][Message]
        print("\t\t\t\t\t\t\tAck'ed msg #%d" % int.from_bytes(sequenceNum, "big"))
        lastSequenceNum = -1


# Run this function to write received bytes to file
def wFileContent(serverAddrPort, filename, seqByteLen, sequenceNum, message):
    global lastSequenceNum
    if int.from_bytes(sequenceNum, "big") == 0:                                # If new file, create file
        print("From %s: New file transfer initiated!" % repr(serverAddrPort))
        ackMsg = "Rec'd file size %d bytes." % int.from_bytes(message, "big")
        lastSequenceNum = 0
        clientSocket.sendto(lastSequenceNum.to_bytes(seqByteLen, "big") + bytearray(ackMsg, 'utf-8'), serverAddrPort)
        print("\t\t\t\t\t\t\tAck'ed msg #%d" % int.from_bytes(sequenceNum, "big"))
    else:                                                                      # If file content
        print("From %s: Message #%d, %d bytes" % (repr(serverAddrPort), int.from_bytes(sequenceNum, "big"), len(message)))
        ackMsg = "Rec'd %s, %d bytes" % (filename.decode(), len(message))
        if int.from_bytes(sequenceNum, "big") == lastSequenceNum + 1:          # If sequence num is the correct one
            try:
                f = open(filename, "ab+")
                f.write(message)
                f.close()
                clientSocket.sendto(sequenceNum + bytearray(ackMsg, 'utf-8'), serverAddrPort)
                print("\t\t\t\t\t\t\tAck'ed msg #%d" % int.from_bytes(sequenceNum, "big"))
                lastSequenceNum += 1
            except IOError:
                print("Error writing to file %s from wFileContent()." % filename.decode())
        else:                                                                   # Resend ack for last correct sequence
            if lastSequenceNum >= 0:
                clientSocket.sendto(lastSequenceNum.to_bytes(seqByteLen, "big") + bytearray(ackMsg, 'utf-8'), serverAddrPort)
                print("\t\t\t\t\t\t\tAck'ed msg #%d" % int.from_bytes(sequenceNum, "big"))


# Function to call to request file
def requestFile():
    filename = ""
    while len(filename) == 0 or len(filename) > 255:
        print("*******************************\nInput file name with extension:")
        filename = sys.stdin.readline()[:-1]  # delete final \n
        # Windows, Linux, and MacOS have a default maximum file name length of 255, but check just in case
        if len(filename) == 0 or len(filename) > 255:
            print("File name must be less than 256 characters long. Please try again.")
        else:
            if os.path.exists(filename):  # Reject if already have file
                print("Already have file %s", filename)
            else:
                print("Sending file request.")
                message = bytearray("RETR", 'utf-8') + bytearray(filename, 'utf-8')  # message = RETR [Filename]
                clientSocket.sendto(message, serverAddr)


# Client socket
clientSocket = socket(AF_INET, SOCK_DGRAM)

# map socket to function to call when socket is....
readSockFunc = {}  # ready for reading
writeSockFunc = {}  # ready for writing
errorSockFunc = {}  # broken

# function to call when fileTransferServerSocket is ready for reading
readSockFunc[clientSocket] = recvMsg

print("CLIENT RUNNING\nConnecting to serverAddr: %s" % repr(clientSocket))
requestFile()  # Ask for file
# Repeatedly check for messages
timeout = 1       # Seconds to wait before reattempting
timeoutCount = 0  # Counter for resend attempts
while 1:
    readRdySet, writeRdySet, errorRdySet = select(list(readSockFunc.keys()),
                                                  list(writeSockFunc.keys()),
                                                  list(errorSockFunc.keys()),
                                                  timeout)

    if not readRdySet and not writeRdySet and not errorRdySet:
        if timeoutCount == 3:  # If no event after 6 timeouts, quit. Also happens if file is not available.
            print("timeout: no events, connection lost")
            sys.exit()
        else:  # try resending last message
            print("timeout: no events")
            # Ideally we would want to resend last message
        timeoutCount += 1
    for sock in readRdySet:
        timeoutCount = 0
        readSockFunc[sock]()
