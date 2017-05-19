import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import PLS
import checksum
import ack


class StopAndWait:
    BUF_SIZE = 4096  # max size of received packet (ACK)

    def __init__(self, t_sock, dest, time_out, p_loss, file_name_server=" ", file_name_client=" "):
        self.socket = t_sock
        self.dest = dest
        self.time_out = time_out
        self.p_loss = p_loss
        self.time_out_sock = time_out * 100  # Socket timeout is 10 times the packet timeout
        if file_name_server != " ":
            self.gen = pac_gen.PacketGen(file_name_server)
        self.timer = None
        self.socket.settimeout(self.time_out_sock)
        if file_name_client != " ":
            self.file = open(file_name_client, 'ab')

    def send(self):
        packet = (self.gen).gen_packet_from_file()
        while packet:
            print("Sending: packet ", packet.seqno)
            if not PLS.lose_packet(self.p_loss):
                (self.socket).sendto(pick.dumps(packet), self.dest)
            self.timer = threading.Timer(self.time_out, timer_handler, args=(self, packet,))
            self.timer.start()

            # wait for ACK or abort after a long period of time
            while 1:
                ack = None
                addr = None
                try:
                    print("\tWaiting For ACK: packet ", packet.seqno)
                    ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
                except socket.timeout:
                    print("Error: 10 retransmissions of packet have occured yet no ACKs were received. Aborting.")
                    self.timer.cancel()
                    return None

                if addr == self.dest and pick.loads(ack).ackno == packet.seqno:  # correct ACK received
                    print("\tACK received for packet ", packet.seqno)
                    self.timer.cancel()
                    packet = self.gen.gen_packet_from_file()  # update the packet
                    break
                else:
                    print("\tWrong ACK or Wrong sender")
        print("File has been transferred successfully, sending close packet")
        end = (self.gen).gen_close_packet()
        (self.socket).sendto(pick.dumps(end), self.dest)

    def recv_one_packet(self):
        byte, addr = self.socket.recvfrom(self.BUF_SIZE)
        packet = pick.loads(byte)
        print("Received packet ", packet.seqno)
        rec_cksum = packet.cksum
        calc_cksum = checksum.gen_cksum(checksum.string_to_byte_arr(packet.data))
        if rec_cksum != calc_cksum and packet.seqno != 0:
            print("\tBy comparing the checksum received and that calculated: packet corrupted. Discard.")
            return 1

        else:
            if packet.seqno == 0:
                print("Close packet received, file received successfully")
                return 0
            else:
                for i in range(len(packet.data)):
                    self.file.write(packet.data[i])
            self.file.flush()
            ack_packet = ack.Ack(0, packet.seqno)
            self.socket.sendto(pick.dumps(ack_packet), self.dest)
            return 1

    def recv_file(self):
        while 1:
            try:
                val = self.recv_one_packet()
            except socket.timeout:
                print("Timeout: Connection closed unexpectedly")
                self.file.close()
                break

            if not val:
                break


def timer_handler(self, packet):
    # retransmit packet to the same client
    print("\tTimeout: retransmitting packet ", packet.seqno)
    if not PLS.lose_packet(self.p_loss):
        (self.socket).sendto(pick.dumps(packet), self.dest)
    self.timer.cancel()
    self.timer = threading.Timer(self.time_out, timer_handler, args=(self, packet,))
    self.timer.start()


file_name_serevr = 'udp_test_server.txt'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 10021))
dest = ('127.0.0.1', 53416)
time_out = 10
p_loss = 0.666
print("Bound UDP on port 10021...")
server = StopAndWait(sock, dest, time_out, p_loss, file_name_serevr, " ")
server.send()

#
# file_name_client = 'udp_test_client.txt'
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(('127.0.0.1', 53416))
# dest = ('127.0.0.1', 10021)
# timeout = 10
# p_loss = 0.234
# client = StopAndWait(sock, dest, timeout, p_loss, " ", file_name_client)
# client.recv_file()
