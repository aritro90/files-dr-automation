# Files DR Automation

We are using cookiecutter to create a Files migration+activation scipt on the fly with predefined data defined in a yaml. I have added 6 yaml files for example purpse. <br />
The Yamls are : <br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/trev3-to-trev4.yaml for moving the files cluster from trevor-3 PE cluster to trevor-4 PE cluster <br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/trev4-to-trev3.yaml for moving the files cluster from trevor-4 PE cluster to trevor-4 PE cluster
<br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/unplanned-target-trev3.yaml for unplanned failover at cluster trevor-3
<br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/unplanned-target-trev4.yaml for unplanned failover at cluster trevor-4
<br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/deactivate-source-trev3.yaml for deactivating the protection domain at trevor-3. This is needed when you already performed an unplanned failover on the other site(trevor-4) and this site(tervor-3) has just been brought up after a disaster event(down situation).
<br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/deactivate-source-trev4.yaml for deactivating the protection domain at trevor-4. This is needed when you already performed an unplanned failover on the other site(trevor-3) and this site(tervor-4) has just been brought up after a disaster event(down situation).
<br />
<br />
You can change the values in the yamls as per you need <br />

```script_name:``` name of the scipt folder and the script <br />
```Source_Cluster_IP:``` IP address of the Source PE cluster <br />
```Target_Cluster_IP:``` IP address of the Destination PE cluster where the FileServer needs to be moved <br />
```PD_Name:``` Protection Domain Name <br />
```FS_Name:``` FileServer Name <br />
```Source_Cluster_Name:``` Name of the Source PE cluster <br />
```Target_Cluster_Name:``` Name of the Destination PE cluster where the FileServer needs to be moved <br />
```fs_uuid:``` file server uuid, could be collected using "afs info.fileservers" command on one of the CVM <br />
```fs_dns:``` DNS IP to be used by Fileserver when failed over to Destination side.  <br />
```fs_ntp:``` NTP IP to be used by Fileserver when failed over to Destination side  <br />
```fs_int_net_uuid:``` UUID for internal/CVM storage facing network for file server on destination side. uuid can be collected using "acli net.list"(for AHV) command on one of the CVM <br />
```fs_int_net_mask:``` Network Mask for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_int_net_gw:``` Gateway IP for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_int_net_pool:``` IP Pool range for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV.  <br />
```fs_ext_net_uuid:``` UUID ID for external/client facing network for file server on destination side. uuid can be collected using "acli net.list"(for AHV) command on one of the CVM <br />
```fs_ext_net_mask:``` Network Mask for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_ext_net_gw:``` Gateway IP for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_ext_net_pool:``` IP Pool range for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV. <br />

## Requirements 
Need Python3 <br />
Need cookiecutter <br />

## Procedure 

```cookiecutter --config-file ./files-dr-automation/trev3-to-trev4.yaml files-dr-automation --no-input```

As soon as you execute the above command it will create a directory with the script_name and a python script
Note: Similar command can be executed against different yaml files to generate different scripts.

```
#ls -l
total 0
drwxr-xr-x  3 aritro.basu  wheel  96 XXX XX 17:55 trevor-3-to-trevor-4

#cd trevor-3-to-trevor-4
#ls -l
total 32
-rw-r--r--  1 aritro.basu  wheel  13200 XXX 17 17:55 trevor-3-to-trevor-4.py
```
You can execute python script and enter the credentions

```
#python3 trevor-3-to-trevor-4.py
Enter Prism Admin User for Trevor-3 Cluster : admin
Enter Password:
Login to Trevor-3 is successful
Protection Domain NTNX-myfiler Exists
Protection Domain NTNX-myfiler is Active
Remote Site Trevor-4 is configured
FileServer myfiler Exists
FileServer uuid 86384a32-da87-490a-af68-6b71287edbf9 matches with the FileServer myfiler
Enter Prism Admin User for Trevor-4 Cluster : admin
Enter Password:
Login to Trevor-4 is successful
Protection Domain NTNX-myfiler Exists
Target Protection Domain NTNX-myfiler is in desired state (NOT Active)
The uuid 441cd480-b463-484d-b4dd-6c7cadc64635 is for Internal Network Primary
The uuid 441cd480-b463-484d-b4dd-6c7cadc64635 is for External Network Primary
Migrating Protection Domain(PD) NTNX-myfiler to the Remote Cluster Trevor-4
{'metadata': {'grand_total_entities': 0, 'total_entities': 0, 'count': 0}, 'entities': []}
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
Waiting for PD NTNX-myfiler to be activated on cluster Trevor-4
PD NTNX-myfiler is activated now on cluster Trevor-4
Activating FileServer myfiler on Trevor-4
{'taskUuid': 'd8ce86d1-2c92-4809-9e7c-f450186a6722'}
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = File Server activation suspend schedule : Completed  ||  Percentage Complete = 2
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = Attach ISO from NVMs : Completed  ||  Percentage Complete = 34
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = Powering ON NVMs : Completed  ||  Percentage Complete = 42
.....
....
...
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = Bring up NVMs : Completed  ||  Percentage Complete = 47
.....
....
...
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = Sending Restore RPC to NVM : Completed  ||  Percentage Complete = 70
....
...
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = File Server activation suspend schedule : Completed  ||  Percentage Complete = 2
Waiting for FileServer myfiler to be activated on Cluster Trevor-4  ||  Current Ongoing Task = File Server Activate  ||  Percentage Complete = 100
FileServer myfiler is activated now on cluster Trevor-4
```
