#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials


# Select the vSphere to be modified
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# List all VMs and display IP, hostname etc..
vmw.list_vm()

