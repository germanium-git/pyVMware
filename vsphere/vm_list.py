#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials


inputs = 'inputs/vsphere_myvmware.yml'


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# List all VMs and display IP, hostname etc..
vmw.list_vm()

