import numpy as np
class Packet:
	def __init__(self,cksum,len,seqno,data) :
		self.cksum = np.uint16(cksum)
		self.len = np.uint16(len)
		self.seqno = np.uint32(seqno)
		self.data = data
