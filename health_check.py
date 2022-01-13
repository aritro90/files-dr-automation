import paramiko
import getpass
import sys
import time

def main():
    #initializing variables
    count = 0
    files_vip = ""
    fs_list =[]

    # Getting inputs from user
    host = input(f'Enter the Cluster VIP : ')
    password = getpass.getpass(prompt="Enter the CVM Password for nutanix user : ")

    # Getting the virtual ip address of the specified fileserver
    try:
        cvm = paramiko.SSHClient()
        cvm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cvm.connect(host, '22', 'nutanix', password)
        stdin, stdout, stderr = cvm.exec_command('/home/nutanix/minerva/bin/afs info.nvmips')
        lines = stdout.readlines()
        cvm.close()

        for i in lines:
            if i:
                count +=1

        x =0
        flag =0
        while x < count:
            if lines[x].split()[0] == "Fileserver:":
                fs_list.append(lines[x].split()[1])
                flag =1

            x +=1

        if flag == 0:
            sys.exit("No Fileserver found on this cluster")
        length = len(fs_list)
        for i in range(length):
            print(str(i+1) + ":",fs_list[i])
        inp = int(input("Enter a Number for fileserver selection :"))
        if inp in range(1,length):
            fs_name = fs_list[inp-1]
        else:
            sys.exit("Invalid input!")
        
        y=0
        while y < count:
            if lines[y].split()[0] == "Fileserver:":
                if lines[y].split()[1] == fs_name:
                    files_vip = lines[y+3].split()[2]
            y +=1

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
    cvm.close()

if __name__ == "__main__":
    main()
