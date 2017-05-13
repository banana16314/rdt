import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #创建一个socket,SOCK_DGRAM表示UDP

s.bind(('127.0.0.1', 10021))                         #绑定IP地址及端口

print('Bound UDP on 10021...')

while True:
    data, addr = s.recvfrom(1024)   #获得数据和客户端的地址与端口,一次最大接收1024字节
    print('Received from %s:%s.' % addr)
    s.sendto(data.decode('utf-8').upper().encode(), addr)#将数据变成大写送回客户端

