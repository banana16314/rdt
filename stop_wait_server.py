import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import PLS

class StopAndWait : 

    BUF_SIZE = 4096 # max size of received packet (ACK)

    def __init__(self,file_name, t_sock, rec_addr, time_out,p_loss) :
        self.socket         = t_sock
        self.dest           = rec_addr
        self.time_out       = time_out
        self.p_loss 		= p_loss
        self.time_out_sock  = time_out*100 # Socket timeout is 10 times the packet timeout
        self.gen            = pac_gen.PacketGen(file_name)
        self.timer 			= None
        self.socket.settimeout(self.time_out_sock)

    def send(self):
        packet = (self.gen).gen_packet_from_file()
        while packet:
            print ("Sending: packet ", packet.seqno)
            if not PLS.lose_packet(self.p_loss) :
            	(self.socket).sendto(pick.dumps(packet), self.dest)
            self.timer = threading.Timer(self.time_out,timer_handler,args=(self, packet,))
            self.timer.start()
            
            # wait for ACK or abort after a long period of time
            while 1 :
                ack = None
                addr = None
                try :
                    print ("\tWaiting For ACK: packet ", packet.seqno)
                    ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
                except socket.timeout :
                    print ("Error: 10 retransmissions of packet have occured yet no ACKs were received. Aborting.")
                    self.timer.cancel()
                    return None

                if addr == self.dest and pick.loads(ack).ackno == packet.seqno : # correct ACK received
                    print ("\tACK received for packet ", packet.seqno)
                    self.timer.cancel()
                    packet = self.gen.gen_packet_from_file() # update the packet
                    break
                else :
                    print("\tWrong ACK or Wrong sender")
        print ("File has been transferred successfully, sending close packet")
        end = (self.gen).gen_close_packet()
        (self.socket).sendto(pick.dumps(end), self.dest)

def timer_handler(self, packet):
    # retransmit packet to the same client
	print ("\tTimeout: retransmitting packet ", packet.seqno)
	if not PLS.lose_packet(self.p_loss) :
		(self.socket).sendto(pick.dumps(packet), self.dest)
	self.timer.cancel()
	self.timer = threading.Timer(self.time_out,timer_handler,args=(self, packet,))
	self.timer.start()
