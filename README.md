# Files DR Automation

We are using cookiecutter to create a Files migration+activation scipt on the fly with predefined data defined in a yaml. I have added 2 yaml files for example purpse. <br />
The Yamls are : <br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/trev3-to-trev4.yaml for moving the files cluster from trevor-3 PE cluster to trevor-4 PE cluster <br />
https://raw.githubusercontent.com/aritro90/files-dr-automation/main/trev4-to-trev3.yaml for moving the files cluster from trevor-4 PE cluster to trevor-4 PE cluster
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
```fs_dns:``` DNS IP to be used by Fileserver when failed over to Destination side. For example, Multiple IP should be defined as ""10.10.10.10" , "10.10.10.11"" <br />
```fs_ntp:``` NTP IP to be used by Fileserver when failed over to Destination side For example, Multiple IP should be defined as ""10.10.10.10" , "10.10.10.11"" <br />
```fs_int_net_uuid:``` UUID for internal/CVM storage facing network for file server on destination side. uuid can be collected using "acli net.list" command on one of the CVM <br />
```fs_int_net_mask:``` Network Mask for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_int_net_gw:``` Gateway IP for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_int_net_pool:``` IP Pool range for internal/CVM storage facing network for file server on destination side . This should be empty in case of you are using managed network on AHV. For example, the value of IP Pool range can be defined as "10.10.10.20 10.10.10.23" for a 3 nodes Fileserver <br />
```fs_ext_net_uuid:``` UUID ID for external/client facing network for file server on destination side. uuid can be collected using "acli net.list" command on one of the CVM <br />
```fs_ext_net_mask:``` Network Mask for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_ext_net_gw:``` Gateway IP for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV <br />
```fs_ext_net_pool:``` IP Pool range for external/client facing network for file server on destination side . This should be empty in case of you are using managed network on AHV. For example, the value of IP Pool range can be defined as "10.10.20.20 10.10.20.22" for a 3 nodes Fileserver <br />

## Requirements 
Need Python3 <br />
Need cookiecutter <br />

## Procedure 
<br />
`cookiecutter --config-file ./files-dr-automation/trev3-to-trev4.yaml files-dr-automation --no-input`

`# ls -l
total 0
drwxr-xr-x  3 aritro.basu  wheel  96 Dec 17 17:55 trevor-3-to-trevor-4`

`# cd trevor-3-to-trevor-4
# ls -l
total 16
-rw-r--r--  1 aritro.basu  wheel  6083 Dec 17 17:55 trevor-3-to-trevor-4.py
`
