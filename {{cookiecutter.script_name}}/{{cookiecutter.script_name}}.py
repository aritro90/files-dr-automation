import requests
from requests.auth import HTTPBasicAuth
import getpass
import json
import urllib3
import time
import sys
import logging
from datetime import datetime

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
fs_dns = {{cookiecutter.fs_dns}}
fs_ntp = {{cookiecutter.fs_ntp}}
fs_int_net_uuid = "{{cookiecutter.fs_int_net_uuid}}"
fs_int_net_mask = "{{cookiecutter.fs_int_net_mask}}"
fs_int_net_gw = "{{cookiecutter.fs_int_net_gw}}"
fs_int_net_pool = {{cookiecutter.fs_int_net_pool}} 
fs_ext_net_uuid = "{{cookiecutter.fs_ext_net_uuid}}"
fs_ext_net_mask = "{{cookiecutter.fs_ext_net_mask}}"
fs_ext_net_gw = "{{cookiecutter.fs_ext_net_gw}}"
fs_ext_net_pool = {{cookiecutter.fs_ext_net_pool}}
skip_pd_activate = False
log_name_prefix ="{{cookiecutter.script_name}}"

#Creation of log file and setting the logger handler
filename = datetime.now().strftime(f'{log_name_prefix}_%d_%m_%Y_%H_%M_%S.log')
f = open(filename, "w+")
f.close()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                              '%d-%m-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)

# Logic for interpreting arguments passed during script execution
if len(sys.argv) == 1:
    logger.info("Executing the Script without any arguments")
elif sys.argv[1] == "--retry":
    logger.info("Executing the Script with --retry argument")
    Activity_type = "Unplanned"
else:
    logger.error("invalid Argument : " + sys.argv[1])
    logger.error("Exiting the Script..")
    sys.exit()


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
            logger.info(f"Protection Domain {PD_Name} Exists")
            z = 1
            if i['active'] == True :
                logger.info(f"Protection Domain {PD_Name} is Active")
            else:
                logger.error(f"Protection Domain {PD_Name} is not active.. Exiting the script")
                sys.exit()
            if (Activity_type != "Deactivate"):
                for x in i['remote_site_names']:
                    if x == Target_Cluster_Name :
                        logger.info(f"Remote Site {Target_Cluster_Name} is configured")
                        y = 1
                if y != 1 :
                    logger.error(f"Remote Site {Target_Cluster_Name} is not configured on PD Schedule.. Exiting the script")
                    sys.exit()
    if z != 1 :
        logger.error(f"Protection Domain {PD_Name} does not Exists.. Exiting the script")
        sys.exit()

# Validating the Target Protection Domain paramters and state           
def target_pd_check (User_Name,Password):
    r = requests.get(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    y = 0  
    for i in r.json()['entities']:
        if i['name'] == f'{PD_Name}' :
            logger.info(f"Protection Domain {PD_Name} Exists")
            z = 1
            if i['active'] == False :
                logger.info(f"Target Protection Domain {PD_Name} is in desired state (NOT Active)")
            elif (i['active'] == True and Activity_type == "Unplanned"):
                global skip_pd_activate
                skip_pd_activate = True
            else:
                logger.error(f"Target Protection Domain {PD_Name} is in active state seems to be a split brain condition.. Exiting the script")
                sys.exit()
    if z != 1 :
        logger.error(f"Protection Domain {PD_Name} does not Exists.. Exiting the script")
        sys.exit()
        
# Validating the Target network settings for FileServer       
def target_network_uuid_check (User_Name,Password):
    r = requests.get(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/networks', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    y = 0
    for i in r.json()['entities']:
        if i['uuid'] == f'{fs_int_net_uuid}' :
            logger.info(f"The uuid {fs_int_net_uuid} is for Internal Network " + i['name'])
            z = 1
        if i['uuid'] == f'{fs_ext_net_uuid}' :
            logger.info(f"The uuid {fs_ext_net_uuid} is for External Network " + i['name'])
            y = 1
    if z != 1 :
        if y != 1 :
            logger.error("Both external and internal networks uuids are not found")
            sys.exit()
        else : 
            logger.error(f" Internal network uuid {fs_int_net_uuid} is not found")
            sys.exit()
    if y != 1 :
        logger.error(f" External network uuid {fs_ext_net_uuid} is not found")
        sys.exit()

# Checking FileServer Name and its UUID
def fileserver_check (User_Name,Password):
    r = requests.get(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v1/vfilers', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    z = 0
    for i in r.json()['entities']:
        if i['name'] == FS_Name :
            z = 1
            logger.info(f"FileServer {FS_Name} Exists")
            if i['uuid'] == fs_uuid :
                logger.info(f"FileServer uuid {fs_uuid} matches with the FileServer {FS_Name}")
            else :
                logger.error(f"FileServer uuid {fs_uuid} does not match with the FileServer {FS_Name}")
                sys.exit()
            if i['fileServerState'] == "FS_PD_ACTIVATED":
                logger.info(f"FileServer {FS_Name} is present on {Source_Cluster_Name} , but not in Activated state")
    if z != 1 :
        logger.error(f"FileServer {FS_Name} doesn't Exists, Exiting the Script")
        sys.exit()

def task_status(Cluster_IP,task_id,User_Name,Password):
    r = requests.get(f'https://{Cluster_IP}:9440/PrismGateway/services/rest/v2.0/tasks/{task_id}', auth = HTTPBasicAuth (User_Name, Password), verify=False)
    return r.json()

# Defining Post function for Migration Activity
def post_request_migrate(User_Name,Password):
    payload = {'value' : f'{Target_Cluster_Name}'}
    r = requests.post(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/migrate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    logger.info(f"Migrating Protection Domain(PD) {PD_Name} to the Remote Cluster {Target_Cluster_Name} ")
    return r.json()

# Defining Post function for Activation Activity
def post_request_activate_fs(User_Name, Password):
    payload = {'name': f'{FS_Name}', 'internalNetwork': {'subnetMask': f'{fs_int_net_mask}', 'defaultGateway': f'{fs_int_net_gw}', 'uuid': f'{fs_int_net_uuid}', 'pool': fs_int_net_pool}, 'externalNetworks': [{'subnetMask': f'{fs_ext_net_mask}', 'defaultGateway': f'{fs_ext_net_gw}', 'uuid': f'{fs_ext_net_uuid}', 'pool': fs_ext_net_pool}], 'dnsServerIpAddresses': fs_dns, 'ntpServers': fs_ntp, 'uuid': f'{fs_uuid}'}
    r = requests.post(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/activate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    logger.info(f"Activating FileServer {FS_Name} on {Target_Cluster_Name}")
    return r.json()

# Defining Post function for PD Activation Activity for unplanned failover
def post_request_activate_pd(User_Name, Password):
    payload = {}
    r = requests.post(f'https://{Target_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/activate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    if "value" in r.json():
        if (r.json()['value'] == True):
            logger.info(f"Performing an unplanned failover, Activating Protection Domain {PD_Name} on Cluster {Target_Cluster_Name}")
    else:
        logger.error(r.json()['message'])
        logger.error("Exiting the Script..")
        sys.exit()


# Defining Post function for PD Activation Activity for unplanned failover
def post_request_deactivate_pd(User_Name, Password):
    payload = {}
    r = requests.post(f'https://{Source_Cluster_IP}:9440/PrismGateway/services/rest/v2.0/protection_domains/{PD_Name}/deactivate', data = json.dumps(payload, indent=4), headers = {'Content-type': 'application/json'}, auth = HTTPBasicAuth (User_Name, Password), verify=False)
    if "value" in r.json():
        if (r.json()['value'] == True):
            logger.info(f"Deactivating PD {PD_Name}, which will clean up VM/volume-group entities of PD at {Source_Cluster_Name} Cluster")
    else:
        logger.error(r.json()['message'])

# The below 2 functions Source_Site() and Target_Site() will be used as a bridge get the username and password from Prism_auth() and valiate them get_request() and display the messaging accordingly (for success or failure of auth)
def Source_Site():
    Source = Prism_auth(Source_Cluster_Name)
    login_check = get_request(Source_Cluster_IP,*Source)
    if login_check[1] == 200 :
        logger.info(f"Login to {Source_Cluster_Name} is successful")
    else :
        logger.error(login_check[0])
        logger.error(f"Could not connect to the Cluster {Source_Cluster_Name} .. Exiting the script")
        sys.exit()
    source_pd_check (*Source)
    fileserver_check (*Source)
    return Source
                       
def Target_Site():                  
    Target = Prism_auth(Target_Cluster_Name)
    login_check = get_request(Target_Cluster_IP,*Target)
    if login_check[1] == 200 :
        logger.info(f"Login to {Target_Cluster_Name} is successful")
    else :
        logger.error(login_check[0])
        logger.error(f"Could not connect to the Cluster {Target_Cluster_Name} .. Exiting the script")
        sys.exit()
    target_pd_check(*Target)
    target_network_uuid_check (*Target)
    return Target 

# Calling the above functions and Storing the credentials in the variable to use it for future function calls
if Activity_type == "Planned" :
    cred_source= Source_Site()
    cred_target= Target_Site()

# Invoking for Unplanned Failover
if Activity_type == "Unplanned" :
    cred_target= Target_Site()
    if skip_pd_activate == False:
        post_request_activate_pd(*cred_target)
        
        # Checking the PD is activated on the remote side 
        while (fs_state != "FS_PD_ACTIVATED" and fs_pdStatus != "true"):
            vfiler_reponse = get_request(Target_Cluster_IP,*cred_target)
            logger.info(f"Waiting for PD {PD_Name} to be activated on cluster {Target_Cluster_Name} ")
            time.sleep(2)
            for i in vfiler_reponse[0]['entities']:
                if i['name'] == FS_Name :
                    fs_pdStatus = i['pdStatus']
                    fs_state = i['fileServerState']
        logger.info(f"Target PD {PD_Name} is activated now")
        time.sleep(30)

if Activity_type == "Deactivate" :
    cred_source= Source_Site()
    post_request_deactivate_pd(*cred_source)
    

# Invoking Migration Activity and storing the response
if Activity_type == "Planned" :
    migrate_response = post_request_migrate(*cred_source)
    logger.info(migrate_response)

    # Checking the PD is activated on the remote side 
    while (fs_state != "FS_PD_ACTIVATED" and fs_pdStatus != "true"):
        vfiler_reponse = get_request(Target_Cluster_IP,*cred_target)
        logger.info(f"Waiting for PD {PD_Name} to be activated on cluster {Target_Cluster_Name} ")
        time.sleep(2)
        for i in vfiler_reponse[0]['entities']:
            if i['name'] == FS_Name :
                fs_pdStatus = i['pdStatus']
                fs_state = i['fileServerState']
    logger.info(f"PD {PD_Name} is activated now on cluster {Target_Cluster_Name} ")
    time.sleep(60)
            

# Invoking Filesever Activtaion Activity and Storing the response
if Activity_type == "Planned" or  Activity_type == "Unplanned":
    activate_response = post_request_activate_fs(*cred_target)
    logger.info(activate_response)

    # Checking the FS is activated on the remote side 
    while (fs_state != "FS_ACTIVATED_REACHABLE" and fs_pdstate != "true"):
        vfiler_reponse = get_request(Target_Cluster_IP,*cred_target)
        x = task_status(Target_Cluster_IP,activate_response['taskUuid'],*cred_target)
        while (x['percentage_complete']) != 100:
            x = task_status(Target_Cluster_IP,activate_response['taskUuid'],*cred_target)
            logger.info(f"Waiting for FileServer {FS_Name} to be activated on Cluster {Target_Cluster_Name}  ||  " + "Current Ongoing Task = "+ x['message'] + "  ||  " + "Percentage Complete = "+ str(x['percentage_complete']))
            time.sleep(10)
        for i in vfiler_reponse[0]['entities']:
            if i['name'] == FS_Name :
                fs_pdstate = i['protectionDomainState']
                fs_state = i['fileServerState']
    logger.info(f"FileServer {FS_Name} is activated now on cluster {Target_Cluster_Name} ")


