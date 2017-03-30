from socket import *
ftp_socket = socket(AF_INET, SOCK_STREAM)
#to reuse socket faster. It has very little consequence for ftp client.
ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
ftp_socket.connect(('127.0.0.1', 2180))
ftp_socket.send("STOP".encode())
