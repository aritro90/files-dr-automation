import paramiko
import getpass
import sys

#initializing variables
count = 0
files_vip = ""

# Getting inputs from user
host = input(f'Enter the Cluster VIP : ')
password = getpass.getpass(prompt="Enter the CVM Password for nutanix user : ")
fs_name = input(f'Enter the fileserver name : ')

# Getting the virtual ip address of the specified fileserver
try:
    cvm = paramiko.SSHClient()
    cvm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cvm.connect(host, '22', 'nutanix', password)
    stdin, stdout, stderr = cvm.exec_command('/home/nutanix/minerva/bin/afs info.nvmips')
    lines = stdout.readlines()

    for i in lines:
        if i:
            count +=1

    x =0 
    flag =0
    while x < count:
        if lines[x].split()[0] == "Fileserver:":
            if lines[x].split()[1] == fs_name:
                flag =1
                files_vip = lines[x+3].split()[2]  
        x +=1

    if flag == 0:
        sys.exit("fileserver name not found. Exiting the script")
    
except paramiko.AuthenticationException as error:
    print(error)
    sys.exit("Exiting the script due to authentication issues")

# Building the command with virtual IP address of the file server 
command = 'ssh nutanix@{} "/home/nutanix/minerva/bin/afs smb.health_check"'.format(files_vip)
print (f"Executing SMB health check on fileserver {fs_name} through {files_vip} via one of the CVM")

# Executing the smb health check for fileserver
cvm = paramiko.SSHClient()
cvm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
cvm.connect(host, '22', 'nutanix', password)
stdin, stdout,stderr = cvm.exec_command(command)
result = stdout.read().decode('ascii').strip("\n")
print(result)