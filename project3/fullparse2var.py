#!/bin/lib/python
import re

#The main aim of this program is to parse the .tr file that is extracted after running the .tcl script

#The .tr file name is mentioned here
tr_file = "1m.tr"

#The different variables that are needed for the calculation are defines here
drop_rate_counter1 = 0
packet_id1 = " "
packet_start_time1 = 0.0
latency1 = 0.0
packets_received1 = 0
average_latency1 = 0
drop_rate_counter2 = 0
packet_id2 = " "
packet_start_time2 = 0.0
latency2 = 0.0
packets_received2 = 0
average_latency2 = 0

#The trace file is opened here
with open(tr_file) as trace:
        #Each line is read and stored line by line in a list
        packet_info_list = trace.readlines()
        #For each of these lines since there are two tcp entried that nodes are checked
        for packet_info in packet_info_list:
            #For the starttime we check using the regular expression which starts with an r and must comtain 0 and 1 and tcp
            #if it matches then the start-time is put into a list and the packet id is extracted
            if re.match(r'/+ .* 0 1 tcp', packet_info):
                packet_id1 = packet_info[-2]
                packet_details1 = re.split(' ', packet_info)
                packet_start_time1 = float(packet_details1[1])
            if re.match(r'/+ .* 4 1 tcp', packet_info):
                packet_id2 = packet_info[-2]
                packet_details2 = re.split(' ', packet_info)
                packet_start_time2 = float(packet_details2[1])
            #For latency calculation we check for both the tcp flows their node numbers. If the regular expression matches then
            # The latency is calculatred and the received packets are incremented by 1
            if re.match(r'r .* 2 3 tcp .*'+packet_id1,packet_info):
                packet_details1 = re.split(' ', packet_info)
                latency1 += float(packet_details1[1]) - packet_start_time1;
                packets_received1 += 1
            if re.match(r'r .* 3 6 tcp .*'+packet_id2,packet_info):
                packet_details2 = re.split(' ', packet_info)
                latency2 += float(packet_details2[1]) - packet_start_time2;
                packets_received2 += 1
            #For droprate we check if the pacets have a d in the beginning or not, if yes then the packet count is incremented
            if re.match(r'd .* tcp',packet_info):
                drop_rate_counter1 += 1
            if re.match(r'd .* tcp',packet_info):
                drop_rate_counter2 += 1

#The calculation for both the tcp flows is done here

average_latency1 = latency1/packets_received1
#through_put = packets_received*8.0/100
through_put1 = float(packets_received1*960/100)
#drop_rate = drop_rate_counter/100
drop_rate1 = float(drop_rate_counter1)/float(100)

average_latency2 = latency2/packets_received1
#through_put = packets_received*8.0/100
through_put2 = float(packets_received2*960/100)
#drop_rate = drop_rate_counter/100
drop_rate2 = float(drop_rate_counter2)/float(100)

#Print statements are given here.
print("through put for var1:",through_put1)
print("average_latency for var1:",average_latency1)
print("drop_rate for var1:",drop_rate1)

print("through put var2:",through_put2)
print("average_latency var2:",average_latency2)
print("drop_rate var2:",drop_rate2)
