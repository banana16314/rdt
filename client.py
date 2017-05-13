import socket
import packet as pac
import packet_gen as pac_gen
import pickle as pick
import stop_wait_client as swc
import selective_repeat_client as sr
import go_back_n_client as gbn

BUF_SIZE = 4096

def read_in(file_name) :
	with open(file_name) as f :
		SERVER_IP = f.readline().rstrip('\n')
		SERVER_PORT = int(f.readline())
		CLIENT_IP = f.readline().rstrip('\n')
		CLIENT_PORT = int(f.readline())
		FILE_NAME = f.readline().rstrip('\n')
		REC_WINDOW = int(f.readline())
		TIMEOUT = float(f.readline())
		MODE = f.readline().rstrip('\n')
	return (SERVER_IP,SERVER_PORT,CLIENT_IP,CLIENT_PORT,FILE_NAME,REC_WINDOW, TIMEOUT,MODE)

(SERVER_IP,SERVER_PORT,CLIENT_IP,CLIENT_PORT,FILE_NAME,REC_WINDOW,TIMEOUT,MODE) = read_in("/tmp/client/client.in")
FILE_NAME_ARR = FILE_NAME.split("/")
FILE_DEST = "/tmp/client/" + FILE_NAME_ARR[len(FILE_NAME_ARR)-1]
sock = socket.socket(socket.AF_INET, # Internet
                      socket.SOCK_DGRAM) # UDP
sock.bind((CLIENT_IP,CLIENT_PORT))

gen = pac_gen.PacketGen()
packet = gen.gen_packet(FILE_NAME)
pac_bytes = pick.dumps(packet)

sock.sendto(pac_bytes, (SERVER_IP, SERVER_PORT))
data, addr = sock.recvfrom(BUF_SIZE)
print("New socket received: ",addr)


if MODE == "SW":
	cli = swc.StopAndWait(FILE_DEST,sock, addr, TIMEOUT)
	cli.recv_file()
elif MODE == "SR":
	cli = sr.SelectiveRepeat(FILE_DEST, sock, addr, TIMEOUT, REC_WINDOW)
	cli.recv_file()
elif MODE == "GBN":
	cli = gbn.GBNClient(FILE_DEST, sock, addr, TIMEOUT)
	cli.recv_file()