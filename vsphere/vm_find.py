#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys


# Select the vSphere to be modified
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'
#inputs = 'inputs/vsphere_myvmware.yml'


# Specify manually the distributed port group to be created
vm = raw_input("Virtual machine: ")

# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# Check if the port group already exist
det = vmw.find_vm(vm)
if det:
    print('\n')
    print("VM name:    {0}".format(det.summary.config.name))
    print("UUID:       {0}".format(det.summary.config.uuid))
    print("Host name:  {0}".format(det.summary.guest.hostName))
    print("IP address: {0}".format(det.summary.guest.ipAddress))
    print('\n')
else:
    print('\nVM not found')
#print(det)


