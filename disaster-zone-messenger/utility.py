import csv
import os
from shutil import copyfile
from os import remove
import copy

# check if a router has not already been added to the map
# returns False if it has, True otherwise
def is_router_not_in_map(router_port, map_path):
    with open(map_path, "r") as network_map:
        reader = csv.reader(network_map, delimiter=',')
        
        for row in reader:
            if(row[0] == router_port):
                return False
        return True

def get_next_hop(router_port, dest, message):
    dvr_table_path = "tables/" + str(router_port) + ".csv"
    dvr_table = convert_csv_to_list(dvr_table_path)
    
    num_columns = len(dvr_table[0])
    column_index = 0
    
    for row in xrange(0, num_columns):
        row_item = dvr_table[row][0]
        
        if row_item == dest:
            break
        else:
            column_index += 1
    
    lowest_cost = 99999
    row_index = 0
    
    for item in xrange(1, num_columns):
        item_data = dvr_table[column_index][item]
        
        if(item_data != "NULL" and item_data != ''):
            if int(item_data) < lowest_cost:
                lowest_cost = item_data
                row_index = item
    
    next_hop = dvr_table[0][row_index]
    return next_hop
    
# create the network map CSV
# example output for routers with scan_range = 2
    #   Router:     Connections:
    #   8888        8889 8890
    #   8889        8888 8890
    #   8890        8888 8889 8892
    #   8892        8890 8893 8894
    #   8893        8892 8894
    #   8894        8892 8893
def create_network_map(router_list):
    file_path = "config/network_map.csv"
    
    # create empty CSV
    # check if open for writing later is better (probably is :( )
    network_map = open(file_path, "w+")
    network_map.close
    
    router_maps = []
    
    # create a list of all router-maps
    for router in router_list:
        router_maps.append(router.file_path)
    
    # ensure all paths are correct (they are)
    for router_map in router_maps:
        with open(router_map, "r") as mapping_file:
            reader = csv.reader(mapping_file, delimiter=',')
            
            for row in reader:
                router = row[0]

                if( is_router_not_in_map(router, file_path) ):
                    connections = row[1]
                    with open(file_path, "a+") as network_map:
                        writer = csv.writer(network_map, delimiter=',')
                        writer.writerow([router, connections])
        # delete mapping of this router                
#        os.remove(router_map)

# Returns a list of router nodes, where node is a tuple - (router_port, direct connections)
def get_router_nodes(network_map_path):
    # list of all nodes
    router_nodes = []
    
    with open(network_map_path, "r") as network_map:
        # get a list of all routers and connections, IE - Create nodes
        reader = csv.reader(network_map, delimiter=',')
        
        for row in reader:
            router_node = (row[0], row[1])
            router_nodes.append(router_node)
            
    return router_nodes

def convert_csv_to_list(file_path):
    lookup_table = []
        
    with open(file_path, 'r') as table:
        reader = csv.reader(table, delimiter=',')
            
        for row in reader:
            row_data = []
                
            for item in row:
                row_data.append(item)

            lookup_table.append(row_data)
    return lookup_table

def write_list_to_csv(file_path, lookup_table):
    with open(file_path, "w+") as table:
        writer = csv.writer(table, delimiter=',')
        
        for row in lookup_table:
            writer.writerow(row)
        
def add_dvr_neightbours(router_nodes):
    COST_TO_ROUTER = 1
    
    for node in router_nodes:
        router_port = node[0]
        
        connections = node[1]
        connections = connections.split(' ')
        connections.pop()
        
        file_path = "tables/" + router_port + ".csv"
        lookup_table = convert_csv_to_list(file_path)
        
        for connection in connections:
            port_index = 0
            
            for item in lookup_table[0]:
                if item == connection:
                    break
                else:
                    port_index += 1
                        
            lookup_table[port_index][port_index] = COST_TO_ROUTER
        
        write_list_to_csv(file_path, lookup_table)
            
def create_distance_vector_tables(router_nodes):
    lookup_table = []
    
    row_1 = []
    row_1.append("to -v /via ->")
    ports = []
    
    for node in router_nodes:
        row_1.append(node[0])
        ports.append(node[0])
    
    columns = len(row_1)
    
    
    lookup_table.append(row_1)
    
    for node in router_nodes:
        new_row = [None] * columns
        new_row[0] = node[0]
        lookup_table.append(new_row)
    
    # create list holding a table for each router
    # we're going to assign NULL to each unusable index
    dv_tables = []
    
    for port in ports:
        dv_tables.append( copy.deepcopy(lookup_table) )
    
    for table, port in zip(dv_tables, ports):
        port_index = 0
        
        # find index of our port
        for item in table[0]:
            if(item == port):
                break
            else:
                port_index += 1
        
        for row in xrange(1, columns): 
            table_row = table[row]
            
            if(row == port_index):
                for item in xrange(columns):
                    if(item != 0):
                        table_row[item] = "NULL"
                        
            for item in xrange(columns):
                if(item == port_index):
                    table_row[item] = "NULL"
        
        with open("tables/" + port + ".csv", 'a') as lookup_table_file:
            writer = csv.writer(lookup_table_file, delimiter=',')
        
            for row in table:
                writer.writerow(row)    
    

def alert_neighbours(file_path, connections, router_port):
    COST_TO_ROUTER = 1
    
    neighbour_table = convert_csv_to_list(file_path)
    
    connections = connections.split(' ')
    connections.pop()
    
    print file_path
    print connections
    
    row_length = len(neighbour_table[0])
    
    # Used for coordinates of, "To 8890 via <router_index>" in the table
    router_index = 0
    
    for item in neighbour_table[0]:
        if item == router_port:
            break
        else:
            router_index += 1
    
    
    for connection in connections:
        print "Current connection: " + connection
        connection_file_path = "tables/" + connection + ".csv"
        connection_table = convert_csv_to_list(connection_file_path)
        
        data_changed = False
        
        for row in xrange(1, row_length):
            row_data = neighbour_table[row]

            for item in xrange(1, row_length):
                if item != 0:
                    item_data = row_data[item]
                    
                    if item_data != "NULL" and item_data != '':
                        print "Item data: " + item_data
                        
                        our_data = connection_table[row][router_index]
                        print "Our data: " + str(our_data)
                    
                        if our_data != "NULL":
                            if our_data == '':
                                # make a bool true for changed file
                                data_changed = True
                                print "[" + str(row) + "][" + str(router_index) + "]"
                                connection_table[row][router_index] = int(item_data) + COST_TO_ROUTER
                            elif our_data > item_data:
                                # make a bool true for changed file
                                data_changed = True
                                print "[" + str(row) + "][" + str(router_index) + "]"
                                connection_table[row][router_index] = int(item_data) + COST_TO_ROUTER
        
        if data_changed:
            write_list_to_csv(connection_file_path, connection_table)          
                
# Distance-Vector Routing
def create_dvr_routing_tables():
    # use the network_map
    network_map_path = "config/network_map.csv"
    router_nodes = get_router_nodes(network_map_path)
    
    create_distance_vector_tables(router_nodes)
    add_dvr_neightbours(router_nodes)
    # all routers now have their direct connections
    # we need to share our info with our direct connections now
    for router_node in router_nodes:
        file_path = "tables/" + router_node[0] + ".csv"
        connections = router_node[1]
        
        alert_neighbours(file_path, connections, router_node[0])
    
    
    for router_node in router_nodes:
        file_path = "tables/" + router_node[0] + ".csv"
        connections = router_node[1]
        
        alert_neighbours(file_path, connections, router_node[0])
    
    
    for router_node in router_nodes:
        file_path = "tables/" + router_node[0] + ".csv"
        connections = router_node[1]
        
        alert_neighbours(file_path, connections, router_node[0])
        
        
    for router_node in router_nodes:
        file_path = "tables/" + router_node[0] + ".csv"
        connections = router_node[1]
        
        alert_neighbours(file_path, connections, router_node[0])
    
    for router_node in router_nodes:
        file_path = "tables/" + router_node[0] + ".csv"
        connections = router_node[1]
        
        alert_neighbours(file_path, connections, router_node[0])