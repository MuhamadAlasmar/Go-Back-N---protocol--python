from socket import *
from splitter_function_demo import get_packets
from threading import Timer
import random
eps = 1

timers = [] # list of timers
file_name = "apply.txt"
packets = get_packets(file_name, mss=20)  # get packets
n_packets = len(packets)  # number of packets to be transmitted

# CLIENT parameters
# port number and host name
server_port = 12500
host_name = "192.168.1.3"

# create client socket
client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.settimeout(0.001)

# set time out
timeout = 1     # in second

# Window parameters
N = 3  # window size
Remaining_N = N  # empty window size
sent_pkt_index = -1  # last transmitted pkt index
window_base = 0  # first sent but not yet acknowledged pkt index
timeout_flag = 0


def timeout_event(index):
    global timeout_flag
    print("Timer for packet {} is fired..".format(index))
    timeout_flag = 1


def check_and_retransmit():
    global timeout_flag, window_base, sent_pkt_index, timer
    print('here..')
    # Resend the packets sent after it
    if random.randint(1, 10) > eps:
        client_socket.sendto(packets[window_base].encode(), (host_name, server_port))
    timer = Timer(timeout, timeout_event, args=[window_base])
    timer.start()
    print('pkt', str(window_base), ' is re - transmitted')
    for i in range(window_base + 1, sent_pkt_index + 1):
        if random.randint(1, 10) > eps:
            client_socket.sendto(packets[i].encode(), (host_name, server_port))
        print('pkt', str(i), ' is re - transmitted')


# while not all the packets are transmitted
while sent_pkt_index < n_packets - 1 or window_base < n_packets:
    # Check timeout and retransmit
    if timeout_flag == 1:
        check_and_retransmit()
        timeout_flag = 0

    # while not all packets are transmitted and empty window size is available
    while Remaining_N > 0 and sent_pkt_index < n_packets - 1:
        # index of pkt to be transmitted next
        sent_pkt_index += 1
        # transmit pkt
        if random.randint(0, 10) > eps:
            client_socket.sendto(packets[sent_pkt_index].encode(), (host_name, server_port))
            print('pkt', str(sent_pkt_index), ' is transmitted')
        # Start the timer.. For the oldest sent byt not yet acknowledged packet
        if sent_pkt_index == window_base:
            timer = Timer(timeout, timeout_event, args=[sent_pkt_index])
            timer.start()
        # change empty window size
        Remaining_N -= 1

    # wait for ACKSs
    try:
        message, _ = client_socket.recvfrom(2048)
        # ACK received
        print('From Server:', message.decode())
        # parse ack message to get last correctly received pkt
        ack = message.decode()
        ack_id = int(message[4:])  # last correctly received pkt

        if ack_id >= window_base:
            # Remove timer
            timer.cancel()
            # change the empty window size
            Remaining_N = ack_id - window_base + 1
            # move window base
            window_base = ack_id + 1
            if window_base < n_packets:
                timer = Timer(timeout, timeout_event, args=[window_base])
                timer.start()
    except:  # nothing to do
        pass



