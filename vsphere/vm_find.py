#! /usr/bin/env python

from vsphere import Vsphere
from vsphere import credentials
from vsphere import seldc
import sys
from pprint import pprint

# Select the vSphere to be modified
inputs = seldc(sys.argv[1:])


# Specify manually the VM to be found
vm = raw_input("Virtual machine: ")


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = Vsphere(*cred)


# Check if the VM exists
vminfo = vmw.find_vm(vm)
pprint(vminfo)
