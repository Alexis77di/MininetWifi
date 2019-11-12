# !/usr/bin/python

import os
import time
import matplotlib.pyplot as plt
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch, OVSKernelAP
from mininet.link import TCLink
from mininet.log import setLogLevel, debug
from mininet.cli import CLI

import sys
gnet=None



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

        jitteraxis = []
        plaxis = []
        for i in range(len(jitter)):
            jitteraxis.append(i)
        for i in range(len(pl)):
            plaxis.append(i)
        plt.plot(plaxis, pl)
        plt.xlabel('Repetitions')
        plt.ylabel('Packet Loss (%)')
        plt.title('Packet Loss Percentage via Iperf')
        savename='Packet Loss ' + ph + '.png'
        plt.savefig(savename)
        plt.clf()
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

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:1,3')
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=drop')
    
    car.cmd('ip route add 200.0.10.2 via 200.0.10.100')

    car.cmd('ping -c 25 200.0.10.2 >> ping_car0_phase1 &')

    client.cmd('iperf -s -u -i 1 >> iperf_client_phase1 &')
    car.cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')

    timeout = time.time() + 25
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - startTime >= i:
            car.cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase1')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase1')
            i += 0.5
    

    print "Moving nodes"
    car.moveNodeTo('150,100,0')

    #time.sleep(2)
    print "Applying second phase"

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2,3')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=output:4')


    car.cmd('ping -c 25 200.0.10.2 >> ping_car0_phase2 &')

    client.cmd('iperf -s -u -i 1 >> iperf_client_phase2 &')
    car.cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')

    timeout = time.time() + 25
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - startTime >= i:
            car.cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase2')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase2')
            i += 0.5



    print "Moving nodes"
    car.moveNodeTo('190,100,0')

    #time.sleep(2)
    print "Applying third phase"

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=drop')
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2')

    car.cmd('ping -c 25 200.0.10.2 >> ping_car0_phase3 &')

    client.cmd('iperf -s -u -i 1 >> iperf_client_phase3 &')
    car.cmd('iperf -c 200.0.10.2 -u -i 1 -t 25')

    timeout = time.time() + 25
    startTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - startTime >= i:
            car.cmd('ifconfig bond0 | grep \"bytes\" >> throughput_bytes_car0_phase3')
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> throughput_bytes_client_phase3')
            i += 0.5

def topology():
    "Create a network."
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSKernelSwitch, accessPoint=OVSKernelAP)
    global gnet
    gnet = net

    print "*** Creating nodes"
    car0 = net.addCar('car%s' % (0), wlans=2, ip='10.0.0.%s/8' % (0 + 1), \
    mac='00:00:00:00:00:0%s' % 0, mode='b')


    eNodeB1 = net.addAccessPoint('eNodeB1', ssid='eNodeB1', dpid='1000000000000000', mode='ac', channel='1', position='80,75,0', range=60)
    eNodeB2 = net.addAccessPoint('eNodeB2', ssid='eNodeB2', dpid='2000000000000000', mode='ac', channel='6', position='180,75,0', range=70)
    rsu1 = net.addAccessPoint('rsu1', ssid='rsu1', dpid='3000000000000000', mode='g', channel='11', position='140,120,0', range=50)
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

    client.cmd('ifconfig client-eth0 200.0.10.2')
    car0.cmd('modprobe bonding mode=3')
    car0.cmd('ip link add bond0 type bond')
    car0.cmd('ip link set bond0 address 02:01:02:03:04:08')
    car0.cmd('ip link set car0-eth0 down')
    car0.cmd('ip link set car0-eth0 address 00:00:00:00:00:11')
    car0.cmd('ip link set car0-eth0 master bond0')
    car0.cmd('ip link set car0-wlan0 down')
    car0.cmd('ip link set car0-wlan0 address 00:00:00:00:00:15')
    car0.cmd('ip link set car0-wlan0 master bond0')
    car0.cmd('ip link set car0-wlan1 down')
    car0.cmd('ip link set car0-wlan1 address 00:00:00:00:00:13')
    car0.cmd('ip link set car0-wlan1 master bond0')
    car0.cmd('ip addr add 200.0.10.100/24 dev bond0')
    car0.cmd('ip link set bond0 up')

    """plot graph"""
    net.plotGraph(max_x=250, max_y=250)

    net.startGraph()

    # Uncomment and modify the two commands below to stream video using VLC
    car0.cmdPrint("sudo vlc -vvv bunnyMob.mp4 --sout '#duplicate{dst=rtp{dst=200.0.10.2,port=5004,mux=ts},dst=display}' :sout-keep &")
    client.cmdPrint("sudo vlc rtp://@200.0.10.2:5004 &")

    car0.moveNodeTo('95,100,0')

    os.system('ovs-ofctl del-flows switch')

    time.sleep(3)

    apply_experiment(car0,client,switch)

    # Uncomment the line below to generate the graph that you implemented
    graphic()

    # kills all the xterms that have been opened
    os.system('pkill xterm')

    print "*** Running CLI"
    CLI(net)

    print "*** Stopping network"
    net.stop()

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

