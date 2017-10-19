#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys

# Select the vSphere to be modified
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'

# Specify manually the distributed port group to be created
dportgroup = raw_input("Distributed port group: ")

# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# Check if the port group already exist
vmw.find_dvportgroup(dportgroup)

