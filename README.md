# SDN QoS Priority Controller

## Problem Statement
Implementation of QoS Priority Controller using
SDN concepts with POX controller and Mininet.
High priority traffic (port 5001) gets priority 200
and low priority traffic (port 5002) gets priority 100
using OpenFlow flow rules.

## Tools Used
- Mininet
- POX Controller
- OpenFlow
- iperf
- Wireshark

## Topology
4 hosts connected to 1 switch controlled by POX
- h1 = 10.0.0.1 (high priority sender)
- h2 = 10.0.0.2 (receiver)
- h3 = 10.0.0.3 (low priority sender)
- h4 = 10.0.0.4 (extra host)

## Setup and Execution Steps

### Step 1 - Install Requirements
sudo apt-get install mininet -y
sudo apt-get install iperf -y
sudo apt-get install wireshark -y

### Step 2 - Clone Repository
git clone https://github.com/yourusername/sdn-qos-priority-controller.git

### Step 3 - Copy Controller File
cp qos_controller.py ~/pox/pox/ext/

### Step 4 - Start POX Controller
cd ~/pox
python3 pox.py log.level --DEBUG ext.qos_controller

### Step 5 - Start Mininet
sudo python3 qos_topology.py

### Step 6 - Run Tests
mininet> pingall
mininet> sh ovs-ofctl dump-flows s1
mininet> h2 iperf -s -u -p 5001 &
mininet> h2 iperf -s -u -p 5002 &
mininet> h1 iperf -c 10.0.0.2 -u -p 5001 -b 10M -t 10
mininet> h3 iperf -c 10.0.0.2 -u -p 5002 -b 10M -t 10

## Expected Output
- Flow table shows priority=200 for port 5001
- Flow table shows priority=100 for port 5002
- High priority traffic shows lower jitter
- Low priority traffic shows higher jitter

## QoS Results
| Traffic | Port | Priority | Jitter   | Loss  |
|---------|------|----------|----------|-------|
| HIGH    | 5001 | 200      | 0.016 ms | 0%    |
| LOW     | 5002 | 100      | 0.041 ms | 0.14% |

## Proof of Execution
Screenshots added in /screenshots folder

## References
- Mininet: http://mininet.org
- POX Controller: https://github.com/noxrepo/pox
- OpenFlow: https://opennetworking.org
