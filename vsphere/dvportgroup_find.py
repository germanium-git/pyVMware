#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials


inputs = 'inputs/vsphere.yml'


# Specify manually the distributed port group to be created
dportgroup = raw_input("Distributed port group: ")

# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# Check if the port group already exist
vmw.find_dvportgroup(dportgroup)

