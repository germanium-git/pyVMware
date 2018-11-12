#! /usr/bin/env python

from vsphere import Vsphere
from pyVmomi import vim, vmodl
from vsphere import credentials
from vsphere import seldc
import sys


# Select the vSphere to be modified
inputs = seldc(sys.argv[1:])

# Create an instance of Class vSphere
cred = credentials(inputs)
# Or bypass with custom credentials
# cred = ('10.20.30.40', 'administrator', 'mysecretpassword123')
vmw = Vsphere(*cred)


# Specify manually the VM Group, the name of the VM to be added to the group and the cluster where the group exists
vm_group = ''
while not vm_group:
    vm_group = raw_input("VM Group name: ")
vm_name = ''
while not vm_name:
    vm_name = raw_input("VM name: ")
cluster_name = ''
while not vm_name:
    cluster_name = raw_input("Cluster name: ")

# Find the VM
vm = vmw.get_vm_object(vm_name)
vmid = str(vm)
print(vmid)

# Find the cluster
cluster = vmw.get_cluster_object(cluster_name)

# Find the group NSX-T_controllers
for group in cluster.configurationEx.group:
    if group.name == vm_group:
        vmlist = list(group.vm)
        # Normalize the list; get rid of objects
        vmlist2 = []
        for i in range(len(vmlist)):
            vmlist2.append(str(vmlist[i]))
        if vmid not in vmlist2:
            print('VM will be added to the VM Group')
            group.vm.append(vm)
        else:
            print('Nothing to add')

oper = 'edit'
spec = vim.cluster.ConfigSpecEx(groupSpec=[vim.cluster.GroupSpec(info=group, operation=oper)])
vmw.wait_for_task(cluster.ReconfigureEx(spec=spec, modify=True))