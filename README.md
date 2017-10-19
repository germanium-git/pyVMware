**pyVMware**
--------

Here are a few Python scripts which may be useful to ease operations tasks on vSphere vCenter.

### Dependencies
These are the python modules needed to run the scrips. Install those by using pip
* pyVmomi - it allows you to manage VMware ESXi and vCenter using Python and the VMware vSphere API.
* pyVim - it's used for the connection handling to the Virtualization Management Object Management Infrastructure (VMOMI). pyVim is part of pyVmomi and it’s installed automatically.


### How to use this project
##### Inventory files
All scripts in this repository are ready-to-use. All input parameters including the credentials to authenticate with NSX manager are specified by *.yaml files stored in the input folder. The password is stored there as an optional parameter which can be omited. The password can always be passed as the input parameter at the beginning of script execution.
Update the variables in the file inputs/vsphere_myvmware.yml and rename it to some other name consisting of two parts such as inputs/vsphere_mylab.yml. Note the "mylab" part between underscore and .yml will be used as the argument for specifying the NSX manager. There's the argument -i put when script is being executed. In case of using for instance *_mylab.yml convention the scrips will be executed with -i mylab parameter.

##### dvportgroup_create.py

```sh
$ ./dvportgroup_create.py -i myvmware
```

It creates new distributed port group on a specific distributed switch.

##### dvportgroup_delete.py

```sh
$ ./dvportgroup_delete.py -i myvmware
```
It deletes a distributed port group.



