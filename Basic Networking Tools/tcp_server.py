import socket
import threading

IP = '0.0.0.0'
PORT = 9998

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.bind((IP, PORT))
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')
    
    while True:
        client, address = server.accept()
        print(f'[*] Accepted Connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
    
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        send.sock(b'ACK')
        
if __name__ == '__main__':
    main()

#   First, we pass the IP and PORT we want to listen on & then tell the server to start listening with a maximum backlog of connections being set to 5 ((10))
#   We then put the server into its main loop, where it waits for an incoming connection. When we receive a connection, we receive the client socket in the client varible and the remote connection details in the address variable ((14))
#   We then create a new thread object that points to our handle_client function and pass it the handle_client object as an arguement ((16))
#   We then start the thread to handle the client connection ((17)), at which point the main server loop is ready to accept another connection. 
#   The handle_client function performs the recv() and then sends a simple message back to the client ((19))