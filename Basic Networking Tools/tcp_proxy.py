# A few imports to start. 
# I created a HEXFILTER string that contains ASCII printable characters, if one exists, or a dot (.) if no representation exists.
# I defined a hexdump function that input as bytes or a strong and prints a hexdump to the console. I.e. It will output packet details with both their hexadecimal values and ASCII printable characters.
# This is useful for understanding unknown protocols, finding creds in plaintext protocols and more.


import sys
import socket
import threading

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        
        printable = word.translate(HEX_FILTER)
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth  = length*3
        results.append(f'{i:04x}    {hexa:<{hexwidth}}  {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
    
#   For receiving both local and remote data, we pass in the socket object to be used. We create an empty byte string (buffer) that will accumulate responses from the socket. 
#   ((35)) - By default, we set a 5 second timeout. This may need to be adjusted if we are proxying over a poor connection or internationally etc. 
#   ((40)) - We setup a loop to read response data into the buffer until there is no more data left or we timeout.
#   ((47)) - Finally, we return the byte buffer string to the caller. which could be either a remote or local machine. 

def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

def request_handler(buffer):
    # Perform packet modifications
    return buffer

def response_handler(buffer):
    # Perform packet modifications
    return buffer

# ((62)) - I connect to the remote host.
# ((64)) - We check to make sure we don't need to first initiate a connection to the remote side and request data before going into the main loop.
#          *Some server daemons will expect you to do this (FTP Servers typically send a banner first, for example) 
# ((75)) - Entering the main while True loop, we then use the receive_from function for both sides of the communication. It accepts a connected socket object and performs a receive. 
#          We dump (hexdump) the contents of the packet so we can inspect it for anything interesting. 
# ((72)) - We next hand the output to response_handler function - then send the received buffer to the local client. 

# The remainder of the proxy code is one loop to continously read from he local client, process the data, send it to the remote client, read from the remote client, process the data and then send it. Continuing until no data remains. 

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
            
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[<==] Sent to remote.")
        
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)
            
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")
            
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections")
            break

# ((109)) - Socket created. 
# ((112)) - Binds to the local host and listens.
# ((123)) - The main loop.
# ((130)) - When fresh connections come in, they are handed over to proxy_handler in a new thread, which handles all the sending and receiving.

        
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('Problem On Bind: %r' % e)
        
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    
    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # Print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()