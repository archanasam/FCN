#!/bin/lib/python
import re
# The main aim of this program is to parse the .tr file that is generated when the .tcl file is run

#The .tr file is given as an input
tr_file = "1m.tr"

#The variables for the calculations are define
drop_rate_counter = 0
packet_id = " "
packet_start_time = 0.0
latency = 0.0
packets_received = 0
average_latency = 0

#We open the .tr file as a trace file where we place all the read lines as single line entries
#into a list
with open(tr_file) as trace:
        packet_info_list = trace.readlines()
        #In the list we search for packet information
        for packet_info in packet_info_list:
            #using regular expressions we match if the entry starts with a r fi=ollowed by anythin then a space followed
            #by a zero,space,1,space and tcp, if it does then split the last but one entry to get the packet id and use the 
            #first item in the list ( which is the time) and put it in a list again.
            if re.match(r'/+ .* 0 1 tcp', packet_info):
                packet_id = packet_info[-2]
                packet_details = re.split(' ', packet_info)
                packet_start_time = float(packet_details[1])
            #using regular expressions we match if the next entry that starts with a zero followed by anything then a 2,space
             #3,space,tcp then we use the packet id to match the pacet and calculate the latency by subtracting the current packet time 
            #whose packet id is the same as the packet id in the time list and subtract it , also incrementing the paclets received by 1 since the 
            #packet has been received at the destination.
            if re.match(r'r .* 2 3 tcp .*'+packet_id,packet_info):
                packet_details = re.split(' ', packet_info)
                latency += float(packet_details[1]) - packet_start_time;
                packets_received += 1
            #using the regular expression we check if the next entry in the list start wid a d followed by wnything and them a tcp then 
            #we increment the drop-rate-counter by 1.
            if re.match(r'd .* tcp',packet_info):
                drop_rate_counter += 1

#The different calulations are done here.
average_latency = latency/packets_received
#through_put = packets_received*8.0/100
through_put = float(packets_received*960/100)
#drop_rate = drop_rate_counter/100
drop_rate = float(drop_rate_counter)/float(100)

#print statements
print("through put :",through_put)
print("average_latency :",average_latency)
print("drop_rate :",drop_rate)
