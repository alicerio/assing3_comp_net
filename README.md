# Assignment 3: Packet Filtering in Software Defined Networks

The goal of this assignment was to implement some packet filtering in an SDN. An SDN, also known as a Software Defined Network is a networking paradigm in which the data and control planes are separated from one another. In an SDN, the control plane is implemented by the controller and the data plane by switches. For this assignment we used OpenFlow, which is the de facto SDN standard. The assignment was divided into three tasks. Each of which had a different purpose.

## Environment Setup:
This program is meant to run on Ubuntu with Mininet and POX Controller.

### Installing Mininet:
>*~$ sudo apt install mininet*

To check if it is installed properly – run the below command. This will create a simple test
network and you can use “pingall” command to see if host1 can ping to host2 or not.
>*~$ sudo mn*

### Installing POX controller (through source)
>*~$ git clone http://github.com/noxrepo/pox*

>*~$ cd pox*

>*~/pox$ git checkout dart*

To run pox controller, you need to run the pox.py or debug-pox.py file as below.

>*~/pox$ ./pox.py “your_controller_module”*

### OpenVSSwitch-testcontroller
>*sudo apt-get install openvswitch-testcontroller*
>*sudo ln /usr/bin/ovs-testcontroller /usr/bin/ovs-controller*

## Task 1
Task 1 is to create a Mininet topology as follows:

>[h1]-----{s1}------[h2]

>[h3]-----/   \\------[h4]

### Run Task 1
>*sudo python assign3starter/topos/part1.py --topo part1*

## Task 2
Task two is to implement a firewall with the following rules:
src ip | dst ip | protocol | action
--- | --- | --- | ---
any ipv4 | any ipv4 | icmp | accept
--- | --- | --- | ---
any | any | arp | accept
--- | --- | --- | ---
any ipv4 | any ipv4 | --- | drop

### Run Task 2
The controller file should be in the *~/pox/ext/* directory. To run task 2, use the following on separate terminals:
>*./pox.py part2controller*

>*assignment3/topos/part2.py --topo part2 --controller remote,port=6633*

## Task 3
Task 3 consisted in creating a firewall in a “real” network. It was very similar to task 2 but with a few differences. The routing now is between subnets and each of them has a different firewall.

### Run Task 3
Similarly to Task 2, the controller file should be in the *~/pox/ext/* directory. To run task 3, use the following on separate terminals:
>*./pox.py part3controller*

>*assignment3/topos/part3.py --topo part2 --controller remote,port=6633*
