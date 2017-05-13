import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import ack
import os
import checksum

class GBNClient:
	BUF_SIZE = 4096 # max size of received packet.

	def __init__(self, file_name, sock, server_addr, time_out):
		self.socket        = sock
		self.dest          = server_addr
		self.time_out      = time_out
		self.sock_time_out = time_out*10
		self.file          = open(file_name, 'ab')
		self.socket.settimeout(self.sock_time_out)

		self.expected_seqno = 1 #Assuming the first seqno = 1
		self.last_ackno = -1

	def recv_one_packet(self) :
		byte, addr = (self.socket).recvfrom(self.BUF_SIZE)

		packet = pick.loads(byte)

		if addr == self.dest :
			print("Received packet ", packet.seqno)
			if packet.seqno == 0 :
				return 0
			self.check_packet(packet)
			
			return 1
        
	def check_packet(self, packet) :
		seqno = packet.seqno
		rec_cksum = packet.cksum
		calc_cksum = checksum.gen_cksum(checksum.string_to_byte_arr(packet.data))
		if rec_cksum != calc_cksum and seqno != 0 :
			print ("\tBy comparing the checksum received and that calculated: packet corrupted. Discard.")
		else :
			#Received expected inorder seqno
			if seqno == self.expected_seqno:
				print("Sending ACK for packet ",seqno)
				ack_packet = ack.Ack(0, seqno)
				self.socket.sendto(pick.dumps(ack_packet), self.dest)
				self.last_ackno = seqno

				self.expected_seqno = self.expected_seqno + 1
				for i in range(len(packet.data)) :
					self.file.write(packet.data[i])
				print ("\tFlushing: packet ",packet.seqno)
				self.file.flush()
			#Not expected seno
			else:
				print("Sending DUPLICATE ACK for packet ",self.last_ackno)
				ack_packet = ack.Ack(0, self.last_ackno)
				self.socket.sendto(pick.dumps(ack_packet), self.dest)
    
	def recv_file(self) :
		while 1:
			try:
				in_progress = self.recv_one_packet()
				if not in_progress:
					print("File Received Successfully.")
					self.file.close()
					break
			except self.socket.timeout:
				self.file.close()
				break