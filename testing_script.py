from subprocess import call


# read test_script_params file
def read_params(file_name) :
	with open(file_name) as f :
		SERVER_IP 		= f.readline().rstrip('\n')
		SERVER_PORT 	= int(f.readline())
		CLIENT_IP 		= f.readline().rstrip('\n')
		CLIENT_PORT 	= int(f.readline())
		W_SERVER 		= int(f.readline())
		W_CLIENT 		= int(f.readline())
		T_SERVER 		= int(f.readline())
		T_CLIENT 		= int(f.readline())
		FILE_NAME 		= f.readline().rstrip('\n')
		PLP 			= f.readline().rstrip('\n').split(",")
		INTERFACE		= f.readline().rstrip('\n')
	return (SERVER_IP,SERVER_PORT,CLIENT_IP,CLIENT_PORT,W_SERVER,W_CLIENT
				,T_SERVER,T_CLIENT,FILE_NAME,PLP,INTERFACE)

(SERVER_IP,SERVER_PORT,CLIENT_IP,CLIENT_PORT,W_SERVER,W_CLIENT
				,T_SERVER,T_CLIENT,FILE_NAME,PLP,INTERFACE) = read_params("./test_script_params")


def build_server_in_file(SERVER_PORT,W_SERVER,i,T_SERVER) :
	in_file = open("/tmp/server/server.in",'w')
	in_file.write(SERVER_PORT)
	in_file.write(W_SERVER)
	in_file.write(i)
	in_file.write(T_SERVER)
	in_file.close()

def build_client_in_file(SERVER_IP,SERVER_PORT,CLIENT_PORT,FILE_NAME,W_CLIENT,T_CLIENT) :
	in_file = open("/tmp/client/client.in",'w')
	in_file.write(SERVER_IP)
	in_file.write(SERVER_PORT)
	in_file.write(CLIENT_PORT)
	in_file.write(FILE_NAME)
	in_file.write(W_CLIENT)
	in_file.write(T_CLIENT)
	in_file.close()


output_f = open("statistics.txt")
# for each probability of loss
for i in PLP :
	build_server_in_file(SERVER_PORT,W_SERVER,i,T_SERVER)
	build_client_in_file(SERVER_IP,SERVER_PORT,CLIENT_PORT,FILE_NAME,W_CLIENT,T_CLIENT)
	call(["python3.4","./server.py","&","> /dev/null"])