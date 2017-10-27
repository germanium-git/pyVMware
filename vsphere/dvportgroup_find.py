#! /usr/bin/env python

from vsphere import Vsphere
from vsphere import credentials
from vsphere import seldc
import sys

# Select the vSphere to be modified
inputs = seldc(sys.argv[1:])

# Specify manually the distributed port group to be created
dportgroup = raw_input("Distributed port group: ")

# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = Vsphere(*cred)

# Check if the port group already exist
vmw.find_dvportgroup(dportgroup)

