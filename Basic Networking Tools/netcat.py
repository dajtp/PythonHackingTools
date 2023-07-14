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

