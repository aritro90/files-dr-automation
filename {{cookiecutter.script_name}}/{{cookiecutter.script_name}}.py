import requests
from requests.auth import HTTPBasicAuth
import getpass
import json
import urllib3
import time
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initializing the required variables
Activity_type = "{{cookiecutter.Activity_type}}"
Source_Cluster_IP = "{{cookiecutter.Source_Cluster_IP}}"
Target_Cluster_IP = "{{cookiecutter.Target_Cluster_IP}}"
PD_Name = "{{cookiecutter.PD_Name}}"
FS_Name = "{{cookiecutter.FS_Name}}"
Source_Cluster_Name = "{{cookiecutter.Source_Cluster_Name}}"
Target_Cluster_Name = "{{cookiecutter.Target_Cluster_Name}}"
fs_state = ""   #Global Variables, no values should be assigned to them by default
fs_pdStatus = ""   #Global Variables, no values should be assigned to them by default
fs_pdstate = ""   #Global Variables, no values should be assigned to them by default
fs_uuid = "{{cookiecutter.fs_uuid}}"
fs_dns = "{{cookiecutter.fs_dns}}"
fs_ntp = "{{cookiecutter.fs_ntp}}"
fs_int_net_uuid = "{{cookiecutter.fs_int_net_uuid}}"
fs_int_net_mask = "{{cookiecutter.fs_int_net_mask}}"
fs_int_net_gw = "{{cookiecutter.fs_int_net_gw}}"
fs_int_net_pool = "{{cookiecutter.fs_int_net_pool}}"   #Do not use this variable in the activate payload if using managed network. Ideal way to define the range is (eg: 3 node fs cluster) fs_int_net_pool = "10.20.10.100 10.20.10.103" 
fs_ext_net_uuid = "{{cookiecutter.fs_ext_net_uuid}}"
fs_ext_net_mask = "{{cookiecutter.fs_ext_net_mask}}"
fs_ext_net_gw = "{{cookiecutter.fs_ext_net_gw}}"
fs_ext_net_pool = "{{cookiecutter.fs_ext_net_pool}}"   #Do not use this variable in the activate payload if using managed network. Ideal way to define the range is (eg: 3 node fs cluster) fs_ext_net_pool = "10.10.10.10 10.10.10.12" 

# The below function is used to prompt user to enter username and password. 
def Prism_auth(Site):
    User_Name = input(f'Enter Prism Admin User for {Site} Cluster : ')
    Password = getpass.getpass(prompt="Enter Password: ")
    return User_Name, Password

# Defining Get function to query the fileserver, this is also be used for auth verification purposes. This will be called multiple times for different cluster, hence passing the cluster IP as an argument as well along with Username and Password
def get_request(Cluster_IP,User_Name,Password):
    try:
        r = requests.get(f'https://{Cluster_IP}:9440/PrismGateway/services/rest/v1/vfilers', auth = HTTPBasicAuth (User_Name, Password), verify=False)
        r.raise_for_status()
        return (r.json()), r.status_code
    except requests.exceptions.HTTPError as errh:
        return errh, r.status_code
    except requests.exceptions.ConnectionError as errc:
        return errc, r.status_code
    except requests.exceptions.RequestException as err:
        return err, r.status_code

# Validating the Source Protection Domain paramters and state
def source_pd_check (User_Name,Password):
    r = requests.get(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    y = 0
    for i in r.json()['entities']:
        if i['name'] == f'{PD_Name}' :
            print(f"Protection Domain {PD_Name} Exists")
            z = 1
            if i['active'] == True :
                print(f"Protection Domain {PD_Name} is Active")
            else:
                sys.exit(f"Protection Domain {PD_Name} is not active.. Exiting the script")
            if (Activity_type != "Deactivate"):
                for x in i['remote_site_names']:
                    if x == Target_Cluster_Name :
                        print(f"Remote Site {Target_Cluster_Name} is configured")
                        y = 1
                if y != 1 :
                    sys.exit(f"Remote Site {Target_Cluster_Name} is not configured on PD Schedule.. Exiting the script")
    if z != 1 :
        sys.exit(f"Protection Domain {PD_Name} does not Exists.. Exiting the script")

# Validating the Target Protection Domain paramters and state           
def target_pd_check (User_Name,Password):
    r = requests.get(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    y = 0  
    for i in r.json()['entities']:
        if i['name'] == f'{PD_Name}' :
            print(f"Protection Domain {PD_Name} Exists")
            z = 1
            if i['active'] == False :
                print(f"Target Protection Domain {PD_Name} is in desired state (NOT Active)")
            else:
                sys.exit(f"Target Protection Domain {PD_Name} is in active state seems to be a split brain condition.. Exiting the script")
    if z != 1 :
        sys.exit(f"Protection Domain {PD_Name} does not Exists.. Exiting the script")
        
# Validating the Target network settings for FileServer       
def target_network_uuid_check (User_Name,Password):
    r = requests.get(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/networks', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    y = 0
    for i in r.json()['entities']:
        if i['uuid'] == f'{fs_int_net_uuid}' :
            print(f"The uuid {fs_int_net_uuid} is for Internal Network " + i['name'])
            z = 1
        if i['uuid'] == f'{fs_ext_net_uuid}' :
            print(f"The uuid {fs_ext_net_uuid} is for External Network " + i['name'])
            y = 1
    if z != 1 :
        if y != 1 :
            sys.exit("Both external and internal networks uuids are not found")
        else : 
            sys.exit(f" Internal network uuid {fs_int_net_uuid} is not found")
    if y != 1 :
        sys.exit(f" External network uuid {fs_ext_net_uuid} is not found")
# Checking FileServer Name and its UUID
def fileserver_check (User_Name,Password):
    r = requests.get(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v1/vfilers', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    for i in r.json()['entities']:
        if i['name'] == FS_Name :
            z = 1
            print(f"FileServer {FS_Name} Exists")
            if i['uuid'] == fs_uuid :
                print(f"FileServer uuid {fs_uuid} matches with the FileServer {FS_Name}")
            else :
                sys.exit(f"FileServer uuid {fs_uuid} does not match with the FileServer {FS_Name}")
            if i['fileServerState'] == "FS_PD_ACTIVATED":
                print(f"FileServer {FS_Name} is present on {Source_Cluster_Name} , though not Activated but can be still migrated ")
    if z != 1 :
        sys.exit(f"FileServer {FS_Name} doesn't Exists, Exiting the Script")

def task_status(Cluster_IP,task_id,User_Name,Password):
    r = requests.get(f'https://{Cluster_IP}:9440/PrismGateway/services/rest/v2.0/tasks/{task_id}', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()

# Defining Post function for Migration Activity
def post_request_migrate(User_Name,Password):
    payload = {'value' : f'{Target_Cluster_Name}'}
    r = requests.post(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/migrate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()

# Defining Post function for Activation Activity
def post_request_activate_fs(User_Name, Password):
    payload = {'name': f'{FS_Name}', 'internalNetwork': {'subnetMask': f'{fs_int_net_mask}', 'defaultGateway': f'{fs_int_net_gw}', 'uuid': f'{fs_int_net_uuid}', 'pool': []}, 'externalNetworks': [{'subnetMask': f'{fs_ext_net_mask}', 'defaultGateway': f'{fs_ext_net_gw}', 'uuid': f'{fs_ext_net_uuid}', 'pool': []}], 'dnsServerIpAddresses': [f'{fs_dns}'], 'ntpServers': [f'{fs_ntp}'], 'uuid': f'{fs_uuid}'}
    r = requests.post(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/activate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()

# Defining Post function for PD Activation Activity for unplanned failover
def post_request_activate_pd(User_Name, Password):
    payload = {}
    r = requests.post(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/activate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()

# Defining Post function for PD Activation Activity for unplanned failover
def post_request_deactivate_pd(User_Name, Password):
    payload = {}
    r = requests.post(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/deactivate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()


# The below 2 functions Source_Site() and Target_Site() will be used as a bridge get the username and password from Prism_auth() and valiate them get_request() and display the messaging accordingly (for success or failure of auth)
def Source_Site():
    Source = Prism_auth(Source_Cluster_Name)
    login_check = get_request(Source_Cluster_IP,*Source)
    if login_check[1] == 200 :
        print (f"Login to {Source_Cluster_Name} is successful")
    else :
        print (login_check[0])
        sys.exit(f"Could not connect to the Cluster {Source_Cluster_Name} .. Exiting the script")
    source_pd_check (*Source)
    fileserver_check (*Source)
    return Source
                       
def Target_Site():                  
    Target = Prism_auth(Target_Cluster_Name)
    login_check = get_request(Target_Cluster_IP,*Target)
    if login_check[1] == 200 :
        print (f"Login to {Target_Cluster_Name} is successful")
    else :
        print (login_check[0])
        sys.exit(f"Could not connect to the Cluster {Target_Cluster_Name} .. Exiting the script")
    target_pd_check(*Target)
    target_network_uuid_check (*Target)
    return Target 

# Calling the above functions and Storing the credentials in the variable to use it for future function calls
if Activity_type == "Planned" :
    cred_source= Source_Site()
    cred_target= Target_Site()

if Activity_type == "Unplanned" :
    cred_target= Target_Site()
    pd_activate_unplanned= post_request_activate_pd(*cred_target)
    print(pd_activate_unplanned)
    time.sleep(30)

if Activity_type == "Deactivate" :
    cred_source= Source_Site()
    pd_deactivate= post_request_deactivate_pd(*cred_source)
    print (pd_deactivate)

# Invoking Migration Activity and storing the response
if Activity_type == "Planned" :
    migrate_response = post_request_migrate(*cred_source)
    print (migrate_response)

    # Checking the PD is activated on the remote side 
    while (fs_state != "FS_PD_ACTIVATED" and fs_pdStatus != "true"):
        vfiler_reponse = get_request(Target_Cluster_IP,*cred_target)
        print ("Waiting for PD to be activated on the Remote Site")
        time.sleep(2)
        for i in vfiler_reponse[0]['entities']:
            if i['name'] == FS_Name :
                fs_pdStatus = i['pdStatus']
                fs_state = i['fileServerState']
    print ("Remote PD is activated now")
    time.sleep(30)
            

# Invoking Filesever Activtaion Activity and Storing the response
if Activity_type == "Planned" or  Activity_type == "Unplanned":
    activate_response = post_request_activate_fs(*cred_target)
    print (activate_response)

    # Checking the FS is activated on the remote side 
    while (fs_state != "FS_ACTIVATED_REACHABLE" and fs_pdstate != "true"):
        vfiler_reponse = get_request(Target_Cluster_IP,*cred_target)
        x = task_status(Target_Cluster_IP,activate_response['taskUuid'],*cred_target)
        while (x['percentage_complete']) != 100:
            x = task_status(Target_Cluster_IP,activate_response['taskUuid'],*cred_target)
            print("Waiting for FS to be activated on the Remote Site  ||  " + "Current Ongoing Task = "+ x['message'] + "  ||  " + "Percentage Complete = "+ str(x['percentage_complete']))
            time.sleep(10)
        for i in vfiler_reponse[0]['entities']:
            if i['name'] == FS_Name :
                fs_pdstate = i['protectionDomainState']
                fs_state = i['fileServerState']
    print ("FS is activated now on remote site")



