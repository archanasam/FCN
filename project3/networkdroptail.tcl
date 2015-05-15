#Create a simulator object
set ns [new Simulator]

set tf [open 1m.tr w]
$ns trace-all $tf

#Define a 'finish' procedure
proc finish {} {
        global ns nf tf
        $ns flush-trace
        close $tf
        exit 0
}

#Create six nodes according to the requirements in the project
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#These are the links between the nodes that implement the Droptail queuing algorithm

$ns duplex-link $n1 $n2 1Mb 1ms DropTail
$ns duplex-link $n2 $n5 1Mb 1ms DropTail
$ns duplex-link $n2 $n3 1Mb 1ms DropTail
$ns duplex-link $n3 $n4 1Mb 1ms DropTail
$ns duplex-link $n3 $n6 1Mb 1ms DropTail

#The size of the queue can be varied between 5 and 10. I have taken it as 5

$ns queue-limit $n2 $n3 5

#These are the network connections for all the nodes that are being used by us.

$ns duplex-link-op $n1 $n2 orient right-down
$ns duplex-link-op $n5 $n2 orient right-up
$ns duplex-link-op $n2 $n3 orient right
$ns duplex-link-op $n3 $n4 orient right-up
$ns duplex-link-op $n3 $n6 orient right-down

#Monitor the queue for link (n2-n3). (for NAM)
$ns duplex-link-op $n2 $n3 queuePos 0.5

#This is yhe forst TCP connection that implements the RENO variant from N1 to N4
set tcp [new Agent/TCP/Sack1]
$tcp set class_ 2
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink
$tcp set fid_ 1

#The FTP flow configuration done here

set ftp [new Application/FTP]
$ftp attach-agent $tcp
$ftp set type_ FTP


#UDP connection that goes from N% to N6

set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null
$udp set fid_ 2

#The CBR flow with packet sixe 1000 and the rate as 1mb which needs variations f
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set packet_size_ 1000
$cbr set rate_ 1mb
$cbr set random_ false

#The ftp start is first followed by the CBR flow and the stop times for all

$ns at 0.0 "$ftp start"
$ns at 80.0 "$cbr start"
$ns at 90.0 "$cbr stop"
$ns at 100.0 "$ftp stop"

#Detaching of the tcp link from the node

$ns at 100.5 "$ns detach-agent $n1 $tcp ; $ns detach-agent $n4 $sink"

#Finish time needs to be specified

$ns at 101.0 "finish"

#Run the simulation
$ns run

