import packet
import random

class PacketGen:
	CHUNK_SIZE = 500

	def __init__(self,file_name) :
		self.file = file_name;
		self.seqno = random.randrange(sys.maxint) # randomly generated sequence number

	def open_file(self) :
		


print("success")