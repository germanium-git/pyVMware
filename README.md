**pyVMware**
--------

Here are a few Python scripts which may be useful to ease operations tasks on vSphere vCenter.

pyVmomi allows you to manage VMware ESXi and vCenter using Python and the VMware vSphere API.

First of all, you need a connection to the API. To connect to the vSphere API, we have to import and use the module pyVim, more precise, the pyVim.connect module and the SmartConnect function. pyVim.connect is used for the connection handling (creation, deletion…) to the Virtualization Management Object Management Infrastructure (VMOMI). pyVim is part of pyVmomi and it’s installed automatically.



dvportgroup_create.py - It creates new distributed port group on a specific distributed switch

dvportgroup_delete.py - It deletes distributed port group

Note: Don't forget update inventory file with appropriate credentials etc.

