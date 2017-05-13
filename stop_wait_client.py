import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import ack
import os
import checksum

class StopAndWait : 

    BUF_SIZE = 4096 # max size of received packet.

    def __init__(self, file_name, sock, server_addr, time_out) :
        self.socket         = sock
        self.dest           = server_addr
        self.time_out       = time_out
        self.time_out_sock  = time_out*100 # Socket timeout is 10 times the packet timeout
        self.file           = open(file_name, 'ab')
        self.socket.settimeout(self.time_out_sock)

    def recv_one_packet(self):
        byte,addr = self.socket.recvfrom(self.BUF_SIZE)
        packet = pick.loads(byte)
        print("Received packet ", packet.seqno)
        rec_cksum = packet.cksum
        calc_cksum = checksum.gen_cksum(checksum.string_to_byte_arr(packet.data))
        if rec_cksum != calc_cksum and packet.seqno != 0 :
        	print ("\tBy comparing the checksum received and that calculated: packet corrupted. Discard.")
        	return 1

        else :
	        if packet.seqno == 0 :
	        	print ("Close packet received, file received successfully")
	        	return 0
	        else :
	        	for i in range(len(packet.data)) :
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
