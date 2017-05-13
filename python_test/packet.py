import numpy as np

class Packet:
	def __init__(self,len,seqno,data):
		self.cksum = uint16(0)
		self.len = uint16(len)
		self.seqno = uint32(seqno)
		self.data = data
