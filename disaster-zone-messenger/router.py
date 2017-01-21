from socket import *
from utility import get_next_hop
import csv

# TODO:
#   Fix bug with 8890 having two 8889 entries
#   Create map of network by combining all maps

class DisasterRouter:
    def __init__(self, port):
        # Port the server will be running on
        self.PORT = port
        self.HOST = ''
        self.ADDR = (self.HOST, self.PORT)
        
        # File storing router's connections to create graph
        self.file_path = "config/" + str(port) + ".csv"
        # Number sent with discovery based on version of its csv
        self.sequence_number = 0
        
        # Maximum size of buffer for single message
        # Example: Max size of a single packet's message = 100 chars
        self.BUFFER_SIZE = 4096
        
        self.create_server()
        self.ack_setup()

    # Create Server for router on its port
    def create_server(self):
        HOST = self.HOST
        ADDR = self.ADDR
        self.NAME = "server_" + str(self.PORT)

        with open("log.txt", "a") as myfile:
            myfile.write(str(self.PORT) + ": server started\n")
        
        tcp_ser_socket = socket(AF_INET, SOCK_STREAM)
        tcp_ser_socket.bind(ADDR)
        tcp_ser_socket.listen(5)
        
        self.server_socket = tcp_ser_socket

    def forward_message(self, dest,data):
        HOST = 'localhost'
        PORT = int(dest)
        ADDR = (HOST, PORT)
    
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        tcp_client_socket.connect(ADDR)
        
        packet = data
        
        tcp_client_socket.send(packet)
        tcp_client_socket.close
        
    # Search for routers within scan-range
    def discovery(self):
        SCAN_RANGE = 2;
        HOST = 'localhost'
        
        # Define scan-range for routers
        START_PORT = self.PORT - SCAN_RANGE;
        
        # + 1 due to "in range" being "< END_PORT", not "<= END_PORT"
        END_PORT = self.PORT + SCAN_RANGE + 1;
        
        #print "\nScan range: " + str(START_PORT) + " - " + str(END_PORT - 1)
        
        # Open CSV, read 
        try:
            connected_routers = ""
            router_csv = open(self.file_path, 'r')
            reader = csv.reader(router_csv, delimiter=',')

            for row in reader:
                connected_routers += row[0] + " "
        except:
            connected_routers = " "
        
        discover_message = 'ACK' + 'LF' + str(self.PORT) + 'LF' + connected_routers + 'LF' + str(self.sequence_number)
        
        # Scan all ports in the scan-range for routers
        for port in range(START_PORT, END_PORT):
            if port != self.PORT:
                ADDR = (HOST, port)
                tcp_client_socket = socket(AF_INET, SOCK_STREAM)
                try:
                    tcp_client_socket.connect(ADDR)
                    packet = discover_message
                    tcp_client_socket.send(packet)
                    tcp_client_socket.shutdown()
                    tcp_client_socket.close()
                except:
                    print "No router detected on port " + str(port)
        
        print "Discovery has ended."
        
    # Server enters listening mode indefinitely

    def listen(self):
        tcp_ser_socket = self.server_socket

        while 1:
            tcp_client_socket, addr = tcp_ser_socket.accept()
            self.tcp_client_socket = tcp_client_socket
            
            print self.NAME + ': Connected to ', addr
            
            while 1:
                data = tcp_client_socket.recv(self.BUFFER_SIZE)
                
                # TODO: Break this cluster fuck into a solo method
                if('ACK' in data):             
                    data_entries = data.split('LF')
                    # assign split data into their variables    
                    router_port = data_entries[1]
                    connected_routers = data_entries[2]
                    sequence_number = data_entries[3];
                    
                    # if there are no entries in this router's map, the file
                    # will not be present, it will except and create the first entry
                    try:
                        with open(self.file_path, 'r') as router_csv:
                            reader = csv.reader(router_csv, delimiter=',', quotechar='"')
                        
                            entry_found = False
                            rows = []

                            for row in reader:
                                if router_port == row[0]:
                                    entry_found = True
                                    # Check it's sequence number, compare with new one
                                    if(sequence_number > row[2]):
                                        # Updating entry, does not change our message so we don't
                                        # increment the sequence number
                                        row[1] = connected_routers
                                        row[2] = sequence_number
                                rows.append(row)

                        with open(self.file_path, 'w') as router_csv:
                            writer = csv.writer(router_csv, delimiter=',', quotechar='"')
                            for row in rows:
                                writer.writerow(row)

                        if not entry_found:
                            # Append entry to CSV    
                            router_csv = open(self.file_path, 'a')
                            csv_w = csv.writer(router_csv, delimiter=',')
                            csv_w.writerow([router_port, connected_routers, sequence_number])

                            # New entry to our map, changing our discovery message,
                            # so we increment our sequence number & run discovery
                            self.sequence_number += 1
                            self.discovery()
                    except:
                        router_csv = open(self.file_path, 'w+')
                        csv_w = csv.writer(router_csv, delimiter=',')
                        
                        csv_w.writerow([router_port, connected_routers, sequence_number])
                        router_csv.close()
                        
                        self.sequence_number += 1
                        self.discovery()
                        
                    with open("log.txt", "a") as myfile:
                        myfile.write(str(self.PORT) + ": " + data[3:] + "\n")
                        # We want to break out of listen after an ACK messsage
                        # to allow client communications to work properly
                        break
                        
                elif('STX' in data):
                    data_list = data.split(',')
                    dest = data_list[0][3:]
                    print "Destination: " + dest 
                    print "Our Port: " + str(self.PORT)
                    
                    if int(dest) == self.PORT:
                        with open("log.txt", "a") as myfile:
                            myfile.write( data[3:] + "\n")
                        print data[3:]
                    else:
                        print "Forwarding message"
                        next_hop = get_next_hop(self.PORT, dest, data)
                        # create packet with new data, and send
                        self.forward_message(next_hop, data)
                        
            tcp_client_socket.close()
        tcp_ser_socket.close()
    
    def ack_setup(self):
        print "Server running on Port", self.PORT