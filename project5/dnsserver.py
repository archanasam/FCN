#! /usr/bin/python

import struct
import sys
import random
import socket
from thread import *
import urllib2
import math

# Location of each replica server
locations = {'52.74.143.5' : ('1.29', '103.86'), # ap-southeast-1
             '52.16.219.28' : ('53.33', '-6.25'), # eu-west-1
             '52.0.73.113' : ('39.04', '-77.49'), # compute-1
             '52.68.12.77' : ('35.69', '139.75'), # ap-northeast-1
             '52.64.63.125' : ('-33.87', '151.21'), # ap-southeast-2
             '52.28.48.84' : ('50.12', '8.68'), # eu-central-1
             '54.94.214.108' : ('-23.55', '-46.64'), # sa-east-1
             '52.11.8.29' : ('45.84', '-119.70'), # us-west-2
             '52.8.12.101' : ('37.34', '-121.89') # us-west-1
            }

# Distance of client from each server
distance = {}

# Get the source IP
def get_src_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("www.ccs.neu.edu", 80))
    return sock.getsockname()[0]


# Calculates the distance between a server and the client
def calc_dist(lat, lon, server_lat, server_lon):
    lat_dist = math.pow((float(lat) - float(server_lat)), 2)
    lon_dist = math.pow((float(lon) - float(server_lon)), 2)

    dist = math.sqrt(lat_dist + lon_dist)

    return dist

# Get the distance of client from the server
def get_distance_from_each_server(lat, lon):
    for server in locations:
        server_location = locations[server]
        server_lat = server_location[0]
        server_lon = server_location[1]

        distance[server] = calc_dist(lat, lon, server_lat, server_lon)


# Get the location of the client
def get_client_lat_lon(ip):
    url = "http://freegeoip.net/csv/" + ip

    reply = None
    try:
        reply = urllib2.urlopen(url)
    except error:
        print "Error in getting location of client. Error: " + str(error)
        return (None, None)

    parts = reply.read().split(",")

    lat = parts[8]
    lon = parts[9]

    return (lat, lon)



# Get the best performing replica server
def get_best_replica(ip):
    lat, lon = get_client_lat_lon(ip)

    if (lat == None or lon == None):
        return None

    get_distance_from_each_server(lat, lon)

    nearest_server = min(distance, key=distance.get)

    return (str(nearest_server))

# Host IP address
host_ip_addr = get_src_ip()

# Port number on which the server runs
if (len(sys.argv) < 5):
        print "Too few arguments."
        print "Usage : ./dnsserver -p <port> -n <name>"
        sys.exit(1)

if (sys.argv[1] != '-p' or sys.argv[3] != '-n'):
        print "Error in arguments."
        print "Usage : ./dnsserver -p <port> -n <name>"
        sys.exit(1)

port = int(sys.argv[2]) #takes port from the command line

# Create socket for server
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #udp socket creation
except socket.error as message:
    print 'Socket creation Failed.' + str(message[0]) + ' Message' + message[1]
    sys.exit()

# Bind the socket to the port
try:
    s.bind((host_ip_addr, port))
except socket.error as message:
    print 'Bind Failed.' + str(message[0]) + ' Message' + message[1]
    sys.exit()



def send_response_to_client(tup, info):
        client_ip = tup[0]
        client_port = tup[1]

        headers = struct.unpack('!6H',info[0:12])    #unpacking the request
        tid = headers[0]
        resp_flags = headers[1]
        questions = headers[2]
        answers = 1
        resp_hdr = struct.pack('!H',tid) + "\x81\x80" + struct.pack('!4H', questions, answers, 0, 0) #packing the response header

        addr = get_best_replica(client_ip)

        # If the address is NULL, return
	if (addr == None):
            return;

        split = addr.split('.')
        ip1 = split[0]
        ip2 = split[1]
        ip3 = split[2]
        ip4 = split[3]
        intip1 = int(ip1)
        intip2 = int(ip2)
        intip3 = int(ip3)
        intip4 = int(ip4)
        qtype = "\x00\x01"
        qclass = "\x00\x01"
        ttl = 10
        length = 4
        resp_hdr += info[12:] + "\xc0\x0c" + qtype + qclass +  struct.pack('!LH4B', ttl, length, intip1,intip2,intip3, intip4) #constructin the entire response
        sent = s.sendto(resp_hdr,(client_ip, client_port)) #sending the response header

while 1:
    info, tup = s.recvfrom(1024)
    
    # Start new thread for each client
    start_new_thread(send_response_to_client ,(tup, info))

# Close the socket
s.close()

