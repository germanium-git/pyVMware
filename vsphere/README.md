**pyVMware**
--------

Here are a few Python scripts which may be useful to ease operations tasks on vSphere vCenter.

pyVmomi allows you to manage VMware ESXi and vCenter using Python and the VMware vSphere API.

First of all, you need a connection to the API. To connect to the vSphere API, we have to import and use the module pyVim, more precise, the pyVim.connect module and the SmartConnect function. pyVim.connect is used for the connection handling (creation, deletion…) to the Virtualization Management Object Management Infrastructure (VMOMI). pyVim is part of pyVmomi and it’s installed automatically.

Note the module tools is this one https://github.com/vmware/pyvmomi-community-samples/tree/master/samples/tools not the one you obtain installing it through pip.
The script was created by modifying the samples provided by pyvmomi-community which are delivered with module tools required.


----------
add_vm_serial_telnet.py - It adds new serial port listening on a specified telnet port

> python add_vm_serial_telnet.py -s *vcenter_ip* -u *username* -p *password* -d cluster -n *vm_name* -t *telnetport*

----------


dvportgroup_create.py - It creates new distributed port group on a specific distributed switch

dvportgroup_delete.py - It deletes distributed port group

Note: Don't forget update inventory file with appropriate credentials etc.

