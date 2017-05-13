import signal
import time
import threading
import time

def timer_handler(thread_name) :
	print ("Thread: ",thread_name)
	# 3,5,4,8,0,9,1,2,7,6

def thread_handler(time_to_wake) :
	t = threading.Timer(time_to_wake,timer_handler,args=(threading.currentThread().getName(),))
	t.start()

threads = list()
times = [3.0, 4.0, 5.0, 1.0, 2.0, 1.0, 6.0, 5.0, 2.0, 3.0]


for i in range(0,10) :
	t = threading.Thread(target=thread_handler,args=(times[i],))
	t.setName(str(i))
	t.start()
	print("Createad thread: ",i)