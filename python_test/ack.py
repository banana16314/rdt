import numpy as np
class ack:
	def __init__(self,len,ackno):
		self.cksum = uint16(0)
		self.len = uint16(len)
		self.ackno = uint32(ackno)
