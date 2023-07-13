import socket

target_host = "127.0.0.1"
target_port = 9998

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the client
client.connect((target_host, target_port))

# Send some data
client.send(b"TCP_CLIENT DATA")

# Receive some data
response = client.recv(4096)

print(response.decode())
client.close()


# Assumptions:
#   - Connection assumed to always succeed (No error handling)
#   - Assumed that we send data first (Some servers send first and await our response)
#   - Assumed the server response will be received quickly (No timeout errors)