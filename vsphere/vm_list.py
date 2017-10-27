#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys


# Select the vSphere instance
inputs = seldc(sys.argv[1:])


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)


# List all VMs and display IP, hostname etc..
vmw.list_vm()
