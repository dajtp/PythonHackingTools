import socket

target_host = "www.google.com"
target_port = 80

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the client
client.connect((target_host, target_port))

# Send some data
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# Receive some data
response = client.recv(4096)

print(response.decode())
client.close()


# Assumptions:
#   - Connection assumed to always succeed (No error handling)
#   - Assumed that we send data first (Some servers send first and await our response)
#   - Assumed the server response will be received quickly (No timeout errors)