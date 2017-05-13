import socket 
import threading 
import random

def handler(data, rec_addr,UDP_IP):
	print("Received data from host ",rec_addr)
	print("data: ", data.decode('UTF-8'))
	print("Sending back ", t.getName())

	# acquire a vacant socket
	t_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	t_sock.bind((UDP_IP,0))
	t_port = t_sock.getsockname()[1]
	print("New socket created on port ",t_port)
	t_sock.sendto(bytes(str(t_port), 'UTF-8'),rec_addr)

	# 

if __name__ == "__main__":

	UDP_IP = "127.0.0.1"
	UDP_PORT = 55555
	buf = 1024

	addr = (UDP_IP,UDP_PORT)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	sock.bind((addr))

	i = 0
	while 1:
		print("Server is listening for connections")
		data, rec_addr = sock.recvfrom(buf)
		# thread.start_new_thread(handler, (data,rec_addr))
		t = threading.Thread(target=handler,args=(data,rec_addr,UDP_IP,))
		t.setName(str(i))
		i = i+1
		t.start()

	serversocket.close()
