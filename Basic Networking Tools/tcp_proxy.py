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