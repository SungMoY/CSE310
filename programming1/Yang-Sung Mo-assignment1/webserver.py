# accept and parse HTTP requests
# retrieve file from server's file system
# create an HTTP response with that file
# send response directly to client
# send HTTP 404 if file not found

# connect via these URLs
# http://{IP4VALUE}:8888/HelloWorld.html
#     {IP4VALUE} is retrieved from running "ipconfig" in cmd
# http://localhost:8888/HelloWorld.html

from socket import *
from signal import *

# sets up ctrl-c to exit via SIGINT
signal(SIGINT, SIG_DFL)

# sets up the server socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# binds socket to port 8888
serverSocket.bind(('', 8888))
# listens for connections
serverSocket.listen()

while True:
    # serverSocket accepts clientSocket
    print("Listening for connections...\n")
    # accept connection
    clientSocket, addr = serverSocket.accept()
    print("Connection accepted from: ", addr, "\n")
    # receive request from client
    message = clientSocket.recv(1024)
    # get the filename from the request
    filename = message.split()[1]
    # try to find the file in the server's file system
    # if file does not exist, respond with 404 Not Found error
    try:
        f = open(filename[1:])
        outputdata = f.read()
        clientSocket.send('HTTP/1.1 200 OK\r\n\r\n'.encode())
        clientSocket.send(outputdata.encode())
        clientSocket.send("\r\n".encode())
        clientSocket.close()
        print("File sent and connection with ", addr, " closed.\n")
    except FileNotFoundError:
        clientSocket.send('HTTP/1.1 404 Not Found\r\n\r\n'.encode())
        clientSocket.close()
        print("File failed to send and connection with ", addr, " closed.\n")
