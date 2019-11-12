# !/usr/bin/python

"""
Task 1: Implementation of the experiment described in the paper with title: 
"From Theory to Experimental Evaluation: Resource Management in Software-Defined Vehicular Networks"
http://ieeexplore.ieee.org/document/7859348/ 
"""

import os
import time
import matplotlib.pyplot as plt
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, OVSKernelAP
from mininet.link import TCLink
from mininet.log import setLogLevel, debug
from mininet.cli import CLI
import itertools


import sys
gnet=None    # if gnet=None for something wrong

# Implement the graphic function in order to demonstrate the network measurements
# Hint: You can save the measurement in an output file and then import it here


def throughput():
    plt.clf()
	
    for l in range(1,4):
        if l== 1:
            ph='phase1'
        elif l==2:
            ph='phase2'
        else:
            ph='phase3'
        carfile='throughput_bytes_car0_'+ph
        clientfile='throughput_bytes_client_'+ph
        car = open(carfile, 'r')
        client = open(clientfile, 'r')
        linescar = car.readlines()
        linesclient = client.readlines()
        sent = []
        difsent = []
        senttimeaxis = []
        x = 0
        #packets sent by car0
        for i in linescar:
            sent.append(int(i.strip().split(':')[2].split(' ')[0]))
            if len(sent) > 1:
                difsent.append(sent[x] - sent[x - 1])
            x += 1
        x=0
        for x in range(len(difsent)):    
            senttimeaxis.append(x)
            x = x + 0.5

        plt.plot(senttimeaxis, difsent)
        plt.xlabel('Seconds')
        plt.ylabel('Sent Data(Bytes)')
        plt.title('Difference between packets sent by car 0')
        savename='Throughput Dif Car0 ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
        senttimeaxis.append(len(sent))
        plt.plot(senttimeaxis, sent)
        plt.xlabel('Seconds')
        plt.ylabel('Sent Data(Bytes)')
        plt.title('Packets sent by car 0')
        savename='Throughput Total Sent Car0 ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()

        received = []
        difreceived = []
        reveivedtimeaxis = []
        x = 0
        for i in linesclient:
            received.append(int(i.strip().split(':')[1].split(' ')[0]))
            if len(received) > 1:
                difreceived.append(received[x] - received[x - 1])
            x += 1
        x=0
        for x in range(len(difreceived)):    
            reveivedtimeaxis.append(x)
            x = x + 0.5

        plt.plot(reveivedtimeaxis, difreceived)
        plt.xlabel('Seconds')
        plt.ylabel('Sent Data(Bytes)')
        plt.title('Difference between packets received by client')
        savename='Throughput Dif client ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
        reveivedtimeaxis.append(len(received))
        plt.plot(reveivedtimeaxis, received)
        plt.xlabel('Seconds')
        plt.ylabel('Sent Data(Bytes)')
        plt.title('Packets received by client')
        savename='Throughput Total Received Car0 ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
        car.close()
        client.close()


def latency():
    plt.clf()
    for l in range(1,4):
        if l==1:
            ph='phase1'
        elif l==2:
            ph='phase2'
        else:
            ph='phase3'
        carfile='ping_car0_'+ph
        #car3file='ping_car3_'+ph
        car=open(carfile,'r')
        linescar=car.readlines()
        #dodge the last 5 lines cause we dont need them and they ruin the split pattern
        #also dodging the 1st line
        ping = []
        pingtimeaxis = []
        lines=len(linescar)-5
        for i in range(1,lines):
            ping.append(float(linescar[i].strip().split('=')[3].split(' ')[0]))
        for i in range(len(ping)):
            pingtimeaxis.append(i)
        if l==1:
            car3=open('ping_car3_phase1','r')
            linescar3=car3.readlines()
            ping3 = []
            pingsum = []
            lines3=len(linescar3)-5
            for j in range(1,lines3):
                ping3.append(float(linescar3[j].strip().split('=')[3].split(' ')[0]))
            pingsum = [x+y for x, y in itertools.izip_longest(ping,ping3,fillvalue=0)]
        if l==1:
            plt.plot(pingtimeaxis, pingsum)
        else:
            plt.plot(pingtimeaxis, ping)
        plt.xlabel('Seconds')
        plt.ylabel('Latency(MS)')
        plt.title('Latency')
        savename='Latency ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
        car.close()


def iperfstuff():
    plt.clf()
    for l in range(1,4):
        if l==1:
            ph='phase1'
        elif l==2:
            ph='phase2'
        else:
            ph='phase3'
        clifile='iperf_client_'+ph
        #car3file='ping_car3_'+ph
        client=open(clifile,'r')
        linescl=client.readlines()
        lines=len(linescl)
        jitter = []
        pl = []
        #dodge the first 7 lines, no usefull data there
        for i in range(7,lines):
            check = linescl[i].split()
            if(len(check))>12:
                if len(check)==14:
                    jitter.append(float(linescl[i].strip().split()[9])) #Jitter
                    pl.append(float(linescl[i].strip().split()[13].split('(')[1].split('%')[0])) #%
                elif len(check)==13:
                    jitter.append(float(linescl[i].strip().split()[8])) #Jitter
                    pl.append(float(linescl[i].strip().split()[12].split('(')[1].split('%')[0])) #%
        if l==1:
            car3f=open('iperf_car3_phase1','r')
            car3=car3f.readlines()
            car3lines=len(car3)
            jitter3=[]
            pl3=[]
            for i in range(7,car3lines):
                check = car3[i].split()
                if(len(check))>12:
                    if len(check)==14:
                        jitter3.append(float(car3[i].strip().split()[9])) #Jitter
                        pl3.append(float(car3[i].strip().split()[13].split('(')[1].split('%')[0])) #%
                    elif len(check)==13:
                        jitter3.append(float(car3[i].strip().split()[8])) #Jitter
                        pl3.append(float(car3[i].strip().split()[12].split('(')[1].split('%')[0])) #%
            jittersum = []
            plsum = []
            jittersum = [x+y for x, y in itertools.izip_longest(jitter,jitter3,fillvalue=0)]
            plsum = [x+y for x, y in itertools.izip_longest(pl,pl3,fillvalue=0)]

        jitteraxis = []
        plaxis = []
        for i in range(len(jitter)):
            jitteraxis.append(i)
        for i in range(len(pl)):
            plaxis.append(i)
        if l==1:
            plt.plot(plaxis, plsum)
        else:
            plt.plot(plaxis, pl)
        plt.xlabel('Repetitions')
        plt.ylabel('Packet Loss (%)')
        plt.title('Packet Loss Percentage via Iperf')
        savename='Packet Loss ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
        if l==1:
            plt.plot(jitteraxis, jittersum)
        else:
            plt.plot(jitteraxis, jitter)
        plt.xlabel('Repetitions')
        plt.ylabel('Jitter(MS)')
        plt.title('Jitter via Iperf')
        savename='Jitter ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()



def graphic():
    latency()
    throughput()
    iperfstuff()



def apply_experiment(car,client,switch):
    
    #time.sleep(2)
    print "Applying first phase"

    ################################################################################ 
    #   1) Add the flow rules below and the necessary routing commands
    #
    #   Hint 1: For the OpenFlow rules you can either delete and add rules
    #           or modify rules (using mod-flows command)       
    #   Example: os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:2')
    #
    #   Hint 2: For the routing commands check the configuration 
    #           at the beginning of the experiment.
    #
    #   2) Calculate Network Measurements using IPerf or command line tools(ifconfig)
    #       Hint: Remember that you can insert commands via the mininet
    #       Example: car[0].cmd('ifconfig bond0 | grep \"TX packets\" >> %s' % output.data)
    #
    #               ***************** Insert code below *********************  
    #################################################################################

    # ---------- Here is the OpenFlow rules ---------- only in port 1 --------------------------------- #


    os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:1')
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=drop')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=drop')
    

    car[0].cmd('ip route add 200.0.10.2 via 200.0.10.50')     #from car0 to client
    client.cmd('ip route add 200.0.10.100 via 200.0.10.150')  #from car3 


    

    timeout = time.time() + 25      # wait for 25 sec  ----->   # https://stackoverflow.com/questions/13293269/how-would-i-stop-a-while-loop-after-n-amount-of-time
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - startTime >= i:
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase1')
            car[0].cmd('ifconfig bond0 | grep \"packets\" >> throughput_packets_car0_phase1')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase1')
            client.cmd('ifconfig client-eth0 | grep \"packets\" >> throughput_packets_client_phase1')
            i += 0.5


    #apo to car0 sto car3 ipolizo statistika me iperf (jitter, packet loss, bandwith, transfer)
    car[3].cmd('iperf -s -u -i 1 >> iperf_car3_phase1 &')
    car[0].cmd('iperf -c 192.168.1.7 -u -i 1 -t 25')

    #apo to car3 telika ston client pou sindeete me to switch
    client.cmd('iperf -s -u -i 1 >> iperf_client_phase1 &')
    car[3].cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')


    #ipologizoume latency kai meta tha ta prosthesoume epidi dn ginete apefthias apo to car0 ston client
    #giati dn iparxei apefthias sindesi meso tou switch
    car[0].cmd('ping -c 25 192.168.1.7 >> ping_car0_phase1 &')
    car[3].cmd('ping -c 25 200.0.10.2 >> ping_car3_phase1 &')





    print "Moving nodes"
    car[0].moveNodeTo('150,100,0')
    car[1].moveNodeTo('120,100,0')
    car[2].moveNodeTo('90,100,0')
    car[3].moveNodeTo('70,100,0')


    #diagrafoume tis sindeseis tou phase 1 afou dn xriazonte pleon
    car[0].cmd('ip route del 200.0.10.2 via 200.0.10.50')
    client.cmd('ip route del 200.0.10.100 via 200.0.10.150')
    
    #time.sleep(2)
    print "Applying second phase"
    ################################################################################ 
    #   1) Add the flow rules below and the necessary routing commands
    #
    #   Hint 1: For the OpenFlow rules you can either delete and add rules
    #           or modify rules (using mod-flows command)       
    #   Example: os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:2')
    #
    #   Hint 2: For the routing commands check the configuration 
    #           you have added before.
    #           Remember that now the car connects to RSU1 and eNodeB2
    #
    #   2) Calculate Network Measurements using IPerf or command line tools(ifconfig)
    #       Hint: Remember that you can insert commands via the mininet
    #       Example: car[0].cmd('ifconfig bond0 | grep \"TX packets\" >> %s' % output.data)
    #
    #           ***************** Insert code below ********************* 
    #################################################################################
    
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2,3')
    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')


    
    #ta idia me to phase 1 me tin diafora oti ta access point sindeonte amesa sto switch
    #kai asxloumaste mono me tis metadoseis tou car0
    

    timeout = time.time() + 25
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - startTime >= i:
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase2')
            car[0].cmd('ifconfig bond0 | grep \"packets\" >> throughput_packets_car0_phase2')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase2')
            client.cmd('ifconfig client-eth0 | grep \"packets\" >> throughput_packets_client_phase2')
            i += 0.5


    client.cmd('iperf -s -u -i 1 >> iperf_client_phase2 &')
    car[0].cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')


    car[0].cmd('ping -c 25 200.0.10.2 >> ping_car0_phase2 &')

    
    print "Moving nodes"
    car[0].moveNodeTo('190,100,0')
    car[1].moveNodeTo('150,100,0')
    car[2].moveNodeTo('120,100,0')
    car[3].moveNodeTo('90,100,0')

    
    #time.sleep(2)
    print "Applying third phase"
    
    ################################################################################ 
    #   1) Add the flow rules below and routing commands if needed
    #
    #   Hint 1: For the OpenFlow rules you can either delete and add rules
    #           or modify rules (using mod-flows command)       
    #   Example: os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:2')
    #
    #
    #   2) Calculate Network Measurements using IPerf or command line tools(ifconfig)
    #       Hint: Remember that you can insert commands via the mininet
    #       Example: car[0].cmd('ifconfig bond0 | grep \"TX packets\" >> %s' % output.data)
    #
    #           ***************** Insert code below ********************* 
    #################################################################################

    #omoios me to phase 2

    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2')
    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=drop')


    timeout = time.time() + 25
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            print " time out"
            time.sleep(5)
            break;
        if time.time() - startTime >= i:
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase3')
            car[0].cmd('ifconfig bond0 | grep \"packets\" >> throughput_packets_car0_phase3')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase3')
            client.cmd('ifconfig client-eth0 | grep \"packets\" >> throughput_packets_client_phase3')
            i += 0.5


    client.cmd('iperf -s -u -i 1 >> iperf_client_phase3 &')
    car[0].cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')


    car[0].cmd('ping -c 25 200.0.10.2 >> ping_car0_phase3 &')



def topology():
    "Create a network."
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch, accessPoint=OVSKernelAP)
    global gnet
    gnet = net


# Here we create the nodes of the topology 

    print "*** Creating nodes"
    car = []
    stas = []
    for x in range(0, 4):
        car.append(x)
        stas.append(x)
    for x in range(0, 4):
        car[x] = net.addCar('car%s' % (x), wlans=2, ip='10.0.0.%s/8' % (x + 1), \
        mac='00:00:00:00:00:0%s' % x, mode='b')

    
    eNodeB1 = net.addAccessPoint('eNodeB1', ssid='eNodeB1', dpid='1000000000000000', mode='ac', channel='1', position='80,75,0', range=60)
    eNodeB2 = net.addAccessPoint('eNodeB2', ssid='eNodeB2', dpid='2000000000000000', mode='ac', channel='6', position='180,75,0', range=70)
    rsu1 = net.addAccessPoint('rsu1', ssid='rsu1', dpid='3000000000000000', mode='g', channel='11', position='140,120,0', range=40)
    c1 = net.addController('c1', controller=RemoteController,ip='10.0.2.15',protocol='tcp',port=6633)
    client = net.addHost ('client')
    switch = net.addSwitch ('switch', dpid='4000000000000000')

    net.plotNode(client, position='125,230,0')
    net.plotNode(switch, position='125,200,0')

    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    print "*** Creating links"
    net.addLink(eNodeB1, switch)
    net.addLink(eNodeB2, switch)
    net.addLink(rsu1, switch)
    net.addLink(switch, client)

    print "*** Starting network"
    net.build()
    c1.start()
    eNodeB1.start([c1])
    eNodeB2.start([c1])
    rsu1.start([c1])
    switch.start([c1])

    for sw in net.vehicles:
        sw.start([c1])

    i = 1
    j = 2
    for c in car:
        c.cmd('ifconfig %s-wlan0 192.168.0.%s/24 up' % (c, i))
        c.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (c, i))
        c.cmd('ip route add 10.0.0.0/8 via 192.168.1.%s' % j)
        i += 2
        j += 2

    i = 1
    j = 2
    for v in net.vehiclesSTA:
        v.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (v, j))
        v.cmd('ifconfig %s-mp0 10.0.0.%s/24 up' % (v, i))
        v.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        i += 1
        j += 2

    for v1 in net.vehiclesSTA:
        i = 1
        j = 1
        for v2 in net.vehiclesSTA:
            if v1 != v2:
                v1.cmd('route add -host 192.168.1.%s gw 10.0.0.%s' % (j, i))
            i += 1
            j += 2

    client.cmd('ifconfig client-eth0 200.0.10.2')
    net.vehiclesSTA[0].cmd('ifconfig car0STA-eth0 200.0.10.50')

    car[0].cmd('modprobe bonding mode=3')
    car[0].cmd('ip link add bond0 type bond')
    car[0].cmd('ip link set bond0 address 02:01:02:03:04:08')
    car[0].cmd('ip link set car0-eth0 down')
    car[0].cmd('ip link set car0-eth0 address 00:00:00:00:00:11')
    car[0].cmd('ip link set car0-eth0 master bond0')
    car[0].cmd('ip link set car0-wlan0 down')
    car[0].cmd('ip link set car0-wlan0 address 00:00:00:00:00:15')
    car[0].cmd('ip link set car0-wlan0 master bond0')
    car[0].cmd('ip link set car0-wlan1 down')
    car[0].cmd('ip link set car0-wlan1 address 00:00:00:00:00:13')
    car[0].cmd('ip link set car0-wlan1 master bond0')
    car[0].cmd('ip addr add 200.0.10.100/24 dev bond0')
    car[0].cmd('ip link set bond0 up')

    car[3].cmd('ifconfig car3-wlan0 200.0.10.150')

    client.cmd('ip route add 192.168.1.8 via 200.0.10.150')
    client.cmd('ip route add 10.0.0.1 via 200.0.10.150')

    net.vehiclesSTA[3].cmd('ip route add 200.0.10.2 via 192.168.1.7')
    net.vehiclesSTA[3].cmd('ip route add 200.0.10.100 via 10.0.0.1')
    net.vehiclesSTA[0].cmd('ip route add 200.0.10.2 via 10.0.0.4')

    car[0].cmd('ip route add 10.0.0.4 via 200.0.10.50')
    car[0].cmd('ip route add 192.168.1.7 via 200.0.10.50')      # 0 -> 3
    car[0].cmd('ip route add 200.0.10.2 via 200.0.10.50')       # 0 -> cl
    car[3].cmd('ip route add 200.0.10.100 via 192.168.1.8')     # 3 -> 0

    """plot graph"""
    net.plotGraph(max_x=250, max_y=250)

    net.startGraph()

    # Uncomment and modify the two commands below to stream video using VLC 
    car[0].cmdPrint("vlc -vvv bunnyMob.mp4 --sout '#duplicate{dst=rtp{dst=200.0.10.2,port=5004,mux=ts},dst=display}' :sout-keep &")
    client.cmdPrint("vlc rtp://@200.0.10.2:5004 &")

    car[0].moveNodeTo('95,100,0')
    car[1].moveNodeTo('80,100,0')
    car[2].moveNodeTo('65,100,0')
    car[3].moveNodeTo('50,100,0')

    os.system('ovs-ofctl del-flows switch')

    time.sleep(3)

    apply_experiment(car,client,switch)

    # Uncomment the line below to generate the graph that you implemented
    graphic()

    # kills all the xterms that have been opened
    os.system('pkill xterm')

    print "*** Running CLI"
    CLI(net)

    print "*** Stopping network"
    net.stop()



# ----- Our main is here ---------- #

if __name__ == '__main__':
    setLogLevel('info')
    try:
        topology()
    except:
        type = sys.exc_info()[0]
        error = sys.exc_info()[1]
        traceback = sys.exc_info()[2]
        print ("Type: %s" % type)
        print ("Error: %s" % error)
        print ("Traceback: %s" % traceback)
        if gnet != None:
            gnet.stop()
        else:
            print "No network was created..."
