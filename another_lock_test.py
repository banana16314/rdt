import threading
import logging
import time
import random

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s',)

lock = threading.Lock()

def method_a(i):
	acquire = lock.acquire(0)
	if not acquire:
		# logging.debug("Not Acquired. %d", i)
		return 1
	else :
		logging.debug("Lock Acquired after %d tries", i)
		rand = random.randint(1,3)
		time.sleep(rand)
		logging.debug("Lock Released.")
		lock.release()
		return 0

def method_b():
	ac = lock.acquire(1)
	i = 0
	while not ac:
		i = i + 1
	logging.debug("%d", i)
	time.sleep(1)
	lock.release()
	logging.debug("LOCK Rel")
def c():
	i = 1
	while 1:
		val = method_a(i)
		if val:
			i = i + 1
		else:
			break

t = threading.Thread(target=method_b, args=( ))
t.setName("B")
t.start()

t2 = threading.Thread(target=c, args=( ))
t2.setName("A")
t2.start()