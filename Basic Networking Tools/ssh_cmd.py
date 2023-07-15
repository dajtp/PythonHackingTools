import paramiko

# Paramiko GitHub: https://github.com/paramiko/paramiko
# Paramiko is a Python produced SSHv2 Protocol. We can use this to build an SSH Client on a system that may not have SSH present. (I.e - Think Windows without privs)

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass
    # user = getpass.getuser()
    user = input('Username: ')
    password = getpass.getpass()
    
    ip = input('Enter Server IP: ') or '192.168.1.146'
    port = input('Enter Port or <CR>: ') or 2222
    cmd = input('Enter Command or <CR>: ') or 'id'
    ssh_command(ip, port, user, password, cmd)