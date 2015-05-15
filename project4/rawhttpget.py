#!/bin/env python

import socket 
import sys 
from struct import * 
import urllib2
import struct
from urlparse import urlparse
import random 
import ntpath
from urlparse import urlparse

# source port to connect to
SRC_PORT = random.randint(2000, 50000)

#ID of the client
ID = random.randint(10000, 50000)

# Sequence numbers
TCP_SEQ_NO = random.randint(2000, 10000)
TCP_ACK_NO = 0

SEND_SEQ_NO = 0
SEND_ACK_NO = 0

RECV_SEQ_NO = 0
RECV_ACK_NO = 0

# Expected sequence number for next reply
EXPECTED_SEQ_NUM = 0

# IP and port information from incoming packet
incoming_pak_src_ip = 0
incoming_pak_src_port = 0

incoming_pak_dest_ip = 0
incoming_pak_dest_port = 0;

recv_flags = 0

# Stores seq_no and corresponding data received from server
# in the message of that seq_no
seq_no_dict = {}

# The contents received from server
server_contents = ""

# Output file to which the data has to written
output_file = ""

recv_iph = 0
recv_tcph = 0


# Initialize 3 way handshake
def initialize_handshake():
    send_syn_msg()
    
    # Receive the SYN-ACK packet
    recv_pack(True)
    
    # Send ACK
    send_ack_msg()


# Send SYN message to server 
def send_syn_msg():
    global TCP_SEQ_NO
    global TCP_ACK_NO
    global syn_req_flags
    global doff
    
    req = ""
    packet = build_packet(TCP_SEQ_NO, TCP_ACK_NO, req, doff, syn_req_flags)
    global send_socket
    send_socket.sendto(packet, (DEST_IP, 0))

# Get the IP header from the packet
def get_iph(packet):
    header = packet[0:20]
    iph = unpack('!BBHHHBBH4s4s', header)
    return iph


# Get the TCP header from the packet
def get_tcph(packet, iph_len):
    header = packet[iph_len: iph_len + 20]
    tcph = unpack('!HHLLBBHHH', header)
    return tcph


# Receive packet from server
def recv_pack(is_syn_ack):
    global recv_socket
    global incoming_pak_src_ip
    global incoming_pak_dest_ip
    global incoming_pak_src_port
    global incoming_pak_dest_port

    packet = recv_socket.recvfrom(65555)
    packet = packet[0]

    global recv_iph
    recv_iph = get_iph(packet)

    version_ihl = recv_iph[0]
    version = version_ihl >> 4
    ttl = recv_iph[5]
    protocol = recv_iph[6]
    ihl = version_ihl & 0xF
    ip_hdr_len = ihl * 4
    incoming_pak_src_ip = socket.inet_ntoa(recv_iph[8])
    incoming_pak_dest_ip = socket.inet_ntoa(recv_iph[9])

    global recv_tcph
    recv_tcph = get_tcph(packet, ip_hdr_len)
    incoming_pak_src_port = recv_tcph[0]
    incoming_pak_dest_port = recv_tcph[1]
    reserved_doff = recv_tcph[4]
    tcp_hdr_len = reserved_doff >> 4
    hdr_size = ip_hdr_len + (tcp_hdr_len * 4)
    data = packet[hdr_size:]

    global server_contents
    server_contents = data

    global size_of_data
    size_of_data = len(data)

    global recv_flags
    recv_flags = recv_tcph[5]

    global RECV_SEQ_NO
    RECV_SEQ_NO = recv_tcph[2]

    global RECV_ACK_NO
    RECV_ACK_NO = recv_tcph[3]

    global SEND_SEQ_NO
    SEND_SEQ_NO = RECV_ACK_NO

    global SEND_ACK_NO
    
    SEND_ACK_NO = RECV_SEQ_NO + size_of_data

    if (is_syn_ack):
	# This is a SYN-ACK and hence add 1 to the Seq No
        SEND_ACK_NO = RECV_SEQ_NO + 1
    else:
	# This is a packet with payload. Add the size
        # of data to Seq No
        SEND_ACK_NO = RECV_SEQ_NO + size_of_data
    	
    return packet


# Send SYN-ACK message with GET request
def send_ack_msg():
    global output_file
    global hostname
    global urlpath
    http_ver = " HTTP/1.0\r\n"
    carriage_return = "\r\n\r\n"

    msg = "GET " + urlpath + http_ver + "Host: " + hostname + carriage_return

    if ( (( len(msg)) % 2 ) !=0 ):
        msg += '\n'

    ack_flags = (0, 1, 0, 0, 1, 0)
    global SEND_SEQ_NO
    global SEND_ACK_NO
    global doff
    packet = build_packet(SEND_SEQ_NO, SEND_ACK_NO, msg, doff, ack_flags)

    global DEST_IP
    send_socket.sendto(packet, (DEST_IP, 0))

    global EXPECTED_SEQ_NUM
    EXPECTED_SEQ_NUM = SEND_ACK_NO


# Build the packet with headers and data
def build_packet( seq_no, ack_no, message, doff, flags):
    ip_header = build_ip_header()
    tcp_header = build_tcp_header( seq_no, ack_no, message, doff, flags)
    packet = ip_header + tcp_header + message
    return packet


# Build IP header
def build_ip_header():
    global ID
    global SRC_IP
    global DEST_IP

    iph_len = 5
    iph_ver = 4
    iph_tos = 0
    iph_total_len = 0
    iph_id = ID + 1
    iph_frag_offset = 0
    iph_ttl = 255
    iph_protocol = socket.IPPROTO_TCP
    iph_chksum = 0
    iph_src_ip_addr = socket.inet_aton(SRC_IP)
    iph_dest_ip_addr = socket.inet_aton(DEST_IP)
    iph_ihl_and_version = (iph_ver << 4) + iph_len

    header = pack('!BBHHHBBH4s4s',
                    iph_ihl_and_version,
                    iph_tos,
                    iph_total_len,
                    iph_id,
                    iph_frag_offset,
                    iph_ttl,
                    iph_protocol,
                    iph_chksum,
                    iph_src_ip_addr,
                    iph_dest_ip_addr)
    return header


# Build TCP header
def build_tcp_header(seq_no, ack_no, message, doff, flags):
    global TCP_SEQ_NO
    TCP_SEQ_NO = seq_no
    TCP_ACK_NO = ack_no
    tcph_src_port = SRC_PORT
    tcph_dest_port = 80
    tcph_len = doff
    
    
    tcp_syn = flags[0]
    tcp_ack = flags[1]
    tcp_fin = flags[2]
    tcp_rst = flags[3]
    tcp_psh = flags[4]
    tcp_urg = flags[5]

    tcph_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)

    tcph_chksm = 0
    tcph_urg_ptr = 0

    tcph_recv_window = socket.htons(5840)
    tcph_len_unused = (tcph_len << 4) + 0

    header = pack('!HHLLBBHHH',
                  tcph_src_port,
                  tcph_dest_port,
                  TCP_SEQ_NO,
                  TCP_ACK_NO,
                  tcph_len_unused,
                  tcph_flags,
                  tcph_recv_window,
                  tcph_chksm,
                  tcph_urg_ptr)

    # Create pseudo TCP header fields
    global SRC_IP
    global DEST_IP
    src_addr = socket.inet_aton(SRC_IP)
    dest_addr = socket.inet_aton(DEST_IP)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    length = len(header) + len(message)

    psh = pack('!4s4sBBH', src_addr, dest_addr, placeholder, protocol, length)
    psh = psh + header + message
    tcph_chksm = checksum(psh)
    header = pack('!HHLLBBH',
                  tcph_src_port,
                  tcph_dest_port,
                  seq_no,
                  ack_no,
                  tcph_len_unused,
                  tcph_flags,
                  tcph_recv_window,
                  ) + pack('H', tcph_chksm) + pack('!H', tcph_urg_ptr)

    return header


# Generate checksum
def checksum(data):
    csum = 0;
    ptr = 0
    length = len(data) % 2

    for i in range(0, len(data) - length, 2):
        csum += ord(data[i]) + (ord(data[i + 1]) << 8)

    if length:
        csum += ord(data[i + 1])

    while (csum >> 16):
        csum = (csum & 0xFFFF) + (csum >> 16)

    csum = ~csum & 0xFFFF
    return csum



# Start the data transmission request
def start_data_req():
    global incoming_pak_src_ip
    global incoming_pak_src_port
    global incoming_pak_dest_ip
    global incoming_pak_dest_port

    global SRC_IP
    global DEST_IP
    global SRC_PORT

    global SEND_ACK_NO
    global RECV_SEQ_NO
    global EXPECTED_SEQ_NUM

    global size_of_data
    global seq_no_dict
    global server_contents
    
    count = 0;

    while True:
        recv_packet = recv_pack(False)

        if ( (incoming_pak_src_ip == DEST_IP)
            and (incoming_pak_dest_ip == SRC_IP)
            and (incoming_pak_dest_port == SRC_PORT)
            and (EXPECTED_SEQ_NUM == RECV_SEQ_NO)
            and (size_of_data > 0)
            and is_checksum_correct(recv_packet)
            and (RECV_SEQ_NO not in seq_no_dict.keys())):

            #print server_contents
            seq_no_dict[RECV_SEQ_NO] = server_contents

            send_data_req()

            global recv_flags
            if ( (recv_flags & 1) == 1):
                end_tcp_conn()
                break
            count += 1


# Check if the received checksum is correct
def is_checksum_correct(packet):
    iph = get_iph(packet)
    version_ihl = iph[0]
    iph_version = version_ihl >> 4
    iph_ihl = version_ihl & 0xF
    iph_len = iph_ihl * 4
    iph_ttl = iph[5]
    iph_protocol = iph[6]
    iph_src_addr = socket.inet_ntoa(iph[8])
    iph_dest_addr = socket.inet_ntoa(iph[9])

    iph_chksum = checksum(packet[0:20])

    tcph = get_tcph(packet, iph_len)

    tcph_src_port = tcph[0]
    tcph_dest_port = tcph[1]
    tcph_seq = tcph[2]
    tcph_ack = tcph[3]
    tcph_reserved_doff = tcph[4]
    tcph_flags = tcph[5]
    tcph_chksum = tcph[7]

    tcph_len = tcph_reserved_doff >> 4

    hdr_size = iph_len + (tcph_len * 4)

    data_size = len(packet) - hdr_size
    data = packet[hdr_size:]

    # Have a TCP header with zero checksum. Build pseudoheader for this
    # and compare with the checksum from the received header
    tcp_hdr_with_zero_chksum = pack('!HHLLBBHHH',
                                        tcph[0],
                                        tcph[1],
                                        tcph[2],
                                        tcph[3],
                                        tcph[4],
                                        tcph[5],
                                        tcph[6],
                                        0,
                                        tcph[8])

    src_addr = iph[8]
    dest_addr = iph[9]
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    length = len(tcp_hdr_with_zero_chksum) + len(data)

    psh = pack('!4s4sBBH', src_addr, dest_addr, placeholder, protocol, length)
    psh = psh + tcp_hdr_with_zero_chksum +  data
    csum = socket.htons(checksum(psh))

    if (iph_chksum == 0 and csum == tcph_chksum):
        return True
    else:
        return False


# Send the request for data transmission
def send_data_req():
    global SEND_SEQ_NO
    global SEND_ACK_NO
    global EXPECTED_SEQ_NUM
    global doff
    global send_socket
    global DEST_IP

    msg = ""
    req_flags = (0, 1, 0, 0, 1, 0) # SYN, ACK, FIN, RST, PSH, URG
    packet = build_packet(SEND_SEQ_NO, SEND_ACK_NO, msg, doff, req_flags)

    send_socket.sendto(packet, (DEST_IP, 0))
    EXPECTED_SEQ_NUM = SEND_ACK_NO


# End the established TCP connection by sending message
# with ACK and FIN flags set
def end_tcp_conn():
    global SEND_SEQ_NO
    global SEND_ACK_NO
    global  DEST_IP

    global doff
    global send_socket

    msg = ""
    fin_flags = (0, 1, 1, 0, 0, 0) # SYN, ACK, FIN, RST, PSH, URG

    packet = build_packet(SEND_SEQ_NO, SEND_ACK_NO, msg, doff, fin_flags)

    send_socket.sendto(packet, (DEST_IP, 0))


# Create the socket to send data
def create_send_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        return sock
    except socket.error, msg:
        print "Error in socket create.\nError : " + str(msg[0]) + "\nError Message: " + msg[1]
        sys.exit(1)



# Create the receive socket
def create_recv_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        sock.settimeout(180)
        return sock
    except socket.error, msg:
        print "Error in socket create.\nError : " + str(msg[0]) + "\nError Message: " + msg[1]
        sys.exit(1)


# Get the destination IP
def get_dest_ip():
    global hostname
    try:
        return socket.gethostbyname(hostname)
    except:
        print "Error in getting dest ip. May be malformed URL"
        sys.exit(1)



# Get the source IP
def get_src_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("www.ccs.neu.edu", 80))
    return sock.getsockname()[0]


# Copy the received contents to the output file
def copy_contents_to_file():
    global seq_no_dict
    string = ''

    for key,value in sorted(seq_no_dict.items()):
        string += str(value)

    string = remove_carriage_return(string)
    store_data_in_file(string)


# Remove the carriage return and new lines from the data
def remove_carriage_return(string):
    index = string.find('\r\n\r\n')
    if index >= 0:
        return string[index + 4:]

    return string



# Store the data in output file
def store_data_in_file(string):
    global output_file
    fp = open(output_file, 'w')
    fp.write(string)
    fp.close()


# Create URL from the input, if it is incomplete
def create_legal_url():
    global input_url
    global hostname

    s = urlparse(input_url)
    if (s.scheme == ""):
        input_url = "http://" + input_url
        x = urlparse(input_url)
        hostname = x.netloc
    else:
        hostname = s.netloc

    get_url_path()


# Get the path of the file within the URL
def get_url_path():
    global input_url
    global hostname
    global urlpath
    global output_file

    s = urlparse(input_url)
    if (s.path == ""):
        urlpath = "/"
        output_file = "index.html"
    else:
        urlpath = s.path
        output_file = ntpath.basename(s.path)
        if (output_file == ""):
            output_file == "index.html"



if (len(sys.argv) != 2):
    print "Usage python rawhttpget.py <URL>"
    sys.exit(1)

input_url = sys.argv[1]
hostname = ""
urlpath = ""

create_legal_url()

DEST_IP = get_dest_ip()
SRC_IP = get_src_ip()

doff = 5
syn_req_flags = (1, 0, 0, 0, 0, 0)

send_socket = create_send_socket()
recv_socket = create_recv_socket()


initialize_handshake()
# At this point, we are done with handshake
# Start sending requests to server
start_data_req()
# Copy all the contents to file
copy_contents_to_file()

