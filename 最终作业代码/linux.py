import socket
client_s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_s.connect('192.168.50.193',12345)
send_connect = 'hihihiconnect'
client_s.send(send_connect.encode('utf-8'))
while True:
    recv_content = client_s.recv(8192)
    list = recv_content.decode().split()
    for i in list:
        print(i)