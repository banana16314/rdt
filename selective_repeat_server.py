import packet_gen as pac_gen
import socket
import pickle as pick
import threading
import pac_ack_t as packt
import PLS
import logging
import math

logging.basicConfig(level=logging.DEBUG,    format='(%(threadName)-9s) %(message)s',)
logging.basicConfig(level=logging.ERROR,    format='(%(threadName)-9s) %(message)s',)
logging.basicConfig(level=logging.WARNING,  format='(%(threadName)-9s) %(message)s',)

class SelectiveRepeat:
    BUF_SIZE = 4096
    CONGEST_LOG = "./congest_log"
    def __init__(self, file_name, t_sock, rec_addr, time_out, p_loss, window_size):
        self.socket        = t_sock
        self.dest          = rec_addr
        self.time_out      = time_out
        self.time_out_sock = time_out*100
        self.gen           = pac_gen.PacketGen(file_name)
        self.p_loss 	   = p_loss
        self.list_size     = window_size 
        self.threshold     = math.floor(window_size/2)
        self.cur_list_size = 1
        self.socket.settimeout(self.time_out_sock)
        self.congest_log   = None
        
        self.lock  = threading.Lock()
        self.packt = packt.PackACKTime()
        self.base_seqno  = -1
        self.init_selective_repeat()

    def init_selective_repeat(self):
        i = 0
        while i < self.cur_list_size:
            self.packt.packet_list.append((self.gen).gen_packet_from_file())
            self.packt.ack_list.append(0)
            self.packt.timer_list.append(None)
            i = i + 1
        self.base_seqno = self.packt.packet_list[0].seqno
        self.congest_log = open(self.CONGEST_LOG + str(self.dest),'w+')
        self.initial_write_to_congestion()
        self.congest_log.write(str(1)+";" + str(self.threshold)+"\n")
        self.congest_log.flush()

    def initial_write_to_congestion(self):
        self.congest_log.write("##;##\n")
        self.congest_log.write("@LiveGraph demo file.\n")
        self.congest_log.write("Window_size;Threshold\n")
        self.congest_log.flush()

    def fix_list(self) :
        if self.cur_list_size < self.threshold :
            next_list_size = 2*self.cur_list_size
            while len(self.packt.unack_window_list) > 0 and self.cur_list_size < next_list_size :
                packet = self.packt.unack_window_list.pop(0)
                self.packt.packet_list.append(packet)
                self.packt.ack_list.append(0)
                self.packt.timer_list.append(None)
                self.send_packet(packet,len(self.packt.packet_list) - 1)
                self.cur_list_size = self.cur_list_size + 1
            while self.cur_list_size < next_list_size :
                packet = self.gen.gen_packet_from_file()
                if packet:
                    self.packt.packet_list.append(packet)
                    self.packt.ack_list.append(0)
                    self.packt.timer_list.append(None)
                    self.send_packet(packet, len(self.packt.packet_list) - 1)
                    self.cur_list_size = self.cur_list_size + 1
                else:
                    break
        else : # cur_list_size exceeded the threshold
            packet = None
            if len(self.packt.unack_window_list) > 0 :
                packet = self.packt.unack_window_list.pop(0)
            else :
                packet = self.gen.gen_packet_from_file()
            if packet:
                self.packt.packet_list.append(packet)
                self.packt.ack_list.append(0)
                self.packt.timer_list.append(None)
                self.send_packet(packet, len(self.packt.packet_list) - 1)
                self.cur_list_size = self.cur_list_size + 1
        self.congest_log.write(str(self.cur_list_size)+";" + str(self.threshold)+"\n")
        self.congest_log.flush()

    def get_index(self,ackno) :
        for i in range(0,len(self.packt.packet_list)) :
            if self.packt.packet_list[i].seqno == ackno :
                return i
        return -1

    def check_list(self, ackno):
        self.lock.acquire()
        index = self.get_index(ackno)
        if index >= 0 :
            # print("Index: ", index, " ackno: ", ackno, " BASE_SEQNO: ", self.base_seqno)
            self.packt.timer_list[index].cancel()
            self.packt.ack_list[index] = 1
            if self.cur_list_size < self.list_size :
                 self.fix_list()
            else :
                self.congest_log.write(str(self.cur_list_size)+";" + str(self.threshold) + "\n")
                self.congest_log.flush()
            if self.packt.ack_list[0] == 1:
                while self.packt.ack_list[0] == 1:
                    self.packt.packet_list.pop(0)
                    self.packt.ack_list.pop(0)
                    self.packt.timer_list.pop(0)

                    packet = None
                    if len(self.packt.unack_window_list) > 0 :
                        packet = self.packt.unack_window_list.pop(0)
                    else :
                        packet = self.gen.gen_packet_from_file()
                    if len(self.packt.packet_list) > 0:
                        self.base_seqno = self.packt.packet_list[0].seqno
                    else:
                        break
                    if packet:
                        self.packt.packet_list.append(packet)
                        self.packt.ack_list.append(0)
                        self.packt.timer_list.append(None)
                        self.send_packet(packet,len(self.packt.packet_list) - 1)

        self.lock.release()

    def wait_for_ack(self):
        # wait for ACK or abort after a long period of time
        while 1 :
            ack = None
            addr = None
            try :
                ack, addr = (self.socket).recvfrom(self.BUF_SIZE)
            except socket.timeout :
                logging.error ("Error: Client have not been responding for server's messages for too long. Aborting.")
                return None

            if addr == self.dest: # correct ACK received
                ackno =  pick.loads(ack).ackno
                logging.debug("\tACK received for packet %d", ackno)
                self.check_list(ackno)
                if len(self.packt.ack_list) == 0:
                    end = (self.gen).gen_close_packet()
                    (self.socket).sendto(pick.dumps(end), self.dest)
                    break
            else :
                logging.error("\tWrong sender")

    def send_packet(self, packet, index):
        logging.debug("Sending: packet %d", packet.seqno)
        if not PLS.lose_packet(self.p_loss) :
            self.socket.sendto(pick.dumps(packet), self.dest)        
        self.packt.timer_list[index] = threading.Timer(self.time_out,self.timer_handler,args=(packet,))
        self.packt.timer_list[index].setName("Timer on packet: "+str(packet.seqno))
        self.packt.timer_list[index].start()

    def send_all_packets(self):
        curr_seqno = 1
        while curr_seqno <= self.cur_list_size:
            self.lock.acquire()
            expected_index = curr_seqno - self.base_seqno
            self.send_packet(self.packt.packet_list[expected_index], expected_index)
            curr_seqno = curr_seqno + 1
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

        self.congest_log.close()

    def timer_handler(self, packet):
        self.lock.acquire()

        logging.warning("\tTimeout: retransmitting packet %d", packet.seqno)      
        for i in range(0,len(self.packt.ack_list)) :
            if not self.packt.ack_list[i] :
                self.packt.timer_list[i].cancel()
                self.packt.unack_window_list.append(self.packt.packet_list[i])

        self.threshold = self.cur_list_size/2
        self.cur_list_size = 1
        self.packt.packet_list = []
        self.packt.ack_list = []
        self.packt.timer_list = []
        self.congest_log.write(str(1)+";" + str(self.threshold)+"\n")
        self.congest_log.flush()

        self.packt.packet_list.append(self.packt.unack_window_list.pop(0))
        self.packt.ack_list.append(0)
        self.packt.timer_list.append(None)

        self.base_seqno = self.packt.packet_list[0].seqno
        self.send_packet(self.packt.packet_list[0],0)

        self.lock.release()


file_name_serevr = 'udp_test_server.txt'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 10021))
dest = ('127.0.0.1', 53416)
time_out = 10
p_loss = 0.123
window_size = 20
print("Bound UDP on port 10021...")
server = SelectiveRepeat(file_name_serevr, sock, dest, time_out, p_loss, window_size)
server.send_file()