import threading
import logging
import time
import random

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)
class locked:
	def __init__(self):
		self.lock = threading.Lock()
	
	def locking_method(self, i):
		if self.lock.acquire(): 
			logging.debug("Lock Acquired after %d tries", i)
			rand = random.randint(1,3)
			time.sleep(rand)
			logging.debug("Lock Released. %s", threading.current_thread().getName())
			self.lock.release()
			return 1
		else :
			return 0

def test(loc):
	i = 1
	while 1:
		v = loc.locking_method(i)
		if not v:
			i = i + 1
		else :
			break

loc = locked()
for i in range(0, 10):
	t = threading.Thread(target=test, args=(loc, ))
	t.setName("Thread " + str(i))
	t.start()
	print("Created Thread ", i)