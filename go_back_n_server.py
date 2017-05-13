import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import GBN_window
import PLS
import math

class GBNServer:
	BUF_SIZE = 4096
	def __init__(self, file_name, t_sock, rec_addr, time_out, p_loss, window_size):
		self.socket        = t_sock
		self.dest          = rec_addr
		self.time_out      = time_out
		self.time_out_sock = time_out*10
		self.gen           = pac_gen.PacketGen(file_name)
		self.p_loss 	   = p_loss
		self.list_size     = window_size
		self.threshold     = math.floor(window_size/2)
		self.cur_list_size = 1 
		self.socket.settimeout(self.time_out_sock)
		
		self.lock  = threading.Lock()
		self.window = GBN_window.GBN_window()
		self.base_seqno  = -1
		self.timer = threading.Timer(self.time_out,self.timer_handler,args=())
		self.init_go_back_n()

	def init_go_back_n(self):
		i = 0
		while i < self.cur_list_size:
			self.window.packet_list.append((self.gen).gen_packet_from_file())
			self.window.ack_list.append(0)
			i = i + 1
		self.base_seqno = self.window.packet_list[0].seqno

	def send_packet(self, packet):
		index = packet.seqno - self.base_seqno
		if index >= 0:
			print("Sending: packet ", packet.seqno)
			if not PLS.lose_packet(self.p_loss) :
				self.socket.sendto(pick.dumps(packet), self.dest)
			# self.packt.timer_list[packet.seqno - self.base_seqno] = threading.Timer(self.time_out,self.timer_handler,args=(packet,))
			# self.packt.timer_list[packet.seqno - self.base_seqno].start()

	def wait_for_ack(self):
		# wait for ACK or abort after a long period of time
		while 1 :
			ack = None
			addr = None
			try :
				ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
			except self.socket.timeout :
				print ("Error: 10 retransmissions of packet have occured yet no ACKs were received. Aborting.")
				return None

			if addr == self.dest: # correct ACK received
				ackno =  pick.loads(ack).ackno
				print ("\tACK received for packet ", ackno)
				self.check_list(ackno)
				if len(self.window.ack_list) == 0:
					end = (self.gen).gen_close_packet()
					# if not PLS.lose_packet(self.p_loss) :
					(self.socket).sendto(pick.dumps(end), self.dest)
					break
			else :
				print("\tWrong sender")

	def send_all_packets(self):
		curr_seqno = 1
		while curr_seqno <= self.cur_list_size:
			self.lock.acquire()

			if curr_seqno == 1:
				self.timer.start() #Start the timer with the base packet

			expected_index = curr_seqno - self.base_seqno
			self.send_packet(self.window.packet_list[expected_index])
			curr_seqno = curr_seqno + 1
			self.lock.release()

	def fix_list(self):
		if self.cur_list_size < self.threshold:
			new_list_size = 2*self.cur_list_size
			while len(self.window.resend_list) > 0 and self.cur_list_size < new_list_size :
				packet = self.window.resend_list.pop(0)
				self.window.packet_list.append(packet)
				self.window.ack_list.append(0)
				self.send_packet(packet)
				self.cur_list_size = self.cur_list_size + 1
			while self.cur_list_size < new_list_size :
				packet = self.gen.gen_packet_from_file()
				if packet:
					self.window.packet_list.append(packet)
					self.window.ack_list.append(0)
					self.send_packet(packet)
					self.cur_list_size = self.cur_list_size + 1
				else:
					break
		else : # cur_list_size exceeded the threshold
			packet = None
			if len(self.window.resend_list) > 0 :
				packet = self.window.resend_list.pop(0)
			else :
				packet = self.gen.gen_packet_from_file()
			if packet:
				self.window.packet_list.append(packet)
				self.window.ack_list.append(0)
				self.send_packet(packet)
				self.cur_list_size = self.cur_list_size + 1

	def check_list(self, ackno):
		self.lock.acquire()

		#seqno is in window
		if ackno >=self.base_seqno and ackno <=self.base_seqno+self.list_size :
	
			#Ack all packets <= ackno (Cumulative Ack)
			i = self.base_seqno
			while i <= ackno:
				self.window.ack_list[i - self.base_seqno] = 1
				i = i + 1
			#Slide window
			# if self.packt.ack_list[0] == 1:
			if self.cur_list_size < self.list_size:
				self.fix_list()
			while self.window.ack_list[0] == 1:
				self.window.packet_list.pop(0)
				self.window.ack_list.pop(0)

				packet = None
				if len(self.window.resend_list) > 0 :
					packet = self.window.resend_list.pop(0)
				else:
					packet = self.gen.gen_packet_from_file()
				if len(self.window.packet_list) > 0:
					self.base_seqno = self.window.packet_list[0].seqno
					#Reset timer for new base
					self.timer.cancel()
					self.timer = threading.Timer(self.time_out,self.timer_handler,args=())
					self.timer.start()
				else:
					# print("WE ARE HERE")
					break
				if packet:
					self.window.packet_list.append(packet)
					self.window.ack_list.append(0)
					if not PLS.lose_packet(self.p_loss) :
						self.socket.sendto(pick.dumps(packet), self.dest)

		self.lock.release()

	def send_file(self):
		sending_all_thread  = threading.Thread(target = self.send_all_packets, args=( ))
		wait_for_ack_thread = threading.Thread(target = self.wait_for_ack, args=( ))
		sending_all_thread.setName("Send All packets.")
		wait_for_ack_thread.setName("Wait for ACK.")
		sending_all_thread.start()
		wait_for_ack_thread.start()

		sending_all_thread.join()
		wait_for_ack_thread.join()

	def timer_handler(self):
		
		self.lock.acquire()
		#Start timer
		#Resend all window
		self.threshold = self.cur_list_size/2

		for i in range(0, len(self.window.packet_list)):
			self.window.resend_list.append(self.window.packet_list[i])

		self.window.packet_list = []
		self.window.ack_list    = []

		self.cur_list_size = 1
		print("Time out resending packet: ", self.base_seqno)
		if len(self.window.resend_list) > 0:
			self.window.packet_list.append(self.window.resend_list[0])
			self.timer = threading.Timer(self.time_out,self.timer_handler,args=())
			self.timer.start()
			self.window.resend_list.pop(0)
			self.window.ack_list.append(0)
			self.base_seqno = self.window.packet_list[0].seqno

			if not PLS.lose_packet(self.p_loss) :
				self.socket.sendto(pick.dumps(self.window.packet_list[0]), self.dest)

		self.lock.release()