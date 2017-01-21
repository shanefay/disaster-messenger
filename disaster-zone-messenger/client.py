from socket import *

HOST = 'localhost'

print "Enter port for this client to communicate over:"
PORT = int(raw_input())

NAME = "client_" + str(PORT) + ": "

print "Enter port you want to talk to:"
dest = raw_input()

ADDR = (HOST, PORT)
tcp_client_socket = socket(AF_INET, SOCK_STREAM)
tcp_client_socket.connect(ADDR)

print "Client running on Port", PORT

while 1:
    print "Enter message to send:"
    userInput = raw_input()
    
    # If the input is empty, continue to take input
    # TODO: Input is now buggy as fuck, check comparison, fix it
    while(userInput == ""):
        print "Empty messages are not allowed\nEnter message to send:"
        userInput = raw_input()
    
    packet = 'STX' + dest + "," + NAME + userInput
    tcp_client_socket.send(packet)
    
tcp_client_socket.close