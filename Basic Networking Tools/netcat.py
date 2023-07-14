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

#   Using the argparse module from the standard library, we create a command line interface. We can provide arguements within the command line, as defined below, when executing our Netcat.py script to run specific functions as described below. 
#   We provide an example of how to use the script which can be invoked by the --help command. 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Net Tool', formatter_class=argparse.RawDescriptionHelpFormatter, 
        epilog=textwrap.dedent('''Example: 
                               netcat.py -t 192.168.1.108 -p 5555 -l -c # Command Shell
                               netcat.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt # Upload a File
                               netcat.py -t 192.168.1.108 -p 5555 -l -e\"cat /etc/password\" # Execute Command
                               echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # Echo Text To Server Port 135
                               netcat.py -t 192.168.1.108 -p 5555 # Connect To Server
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
