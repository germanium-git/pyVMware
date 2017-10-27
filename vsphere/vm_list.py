#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys
from pprint import pprint


# Select the vSphere instance
inputs = seldc(sys.argv[1:])


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)


# List all VMs and display id, uuid, IP, hostname etc..
VMs = vmw.list_vm()
pprint(VMs)
