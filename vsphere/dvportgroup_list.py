#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys

from pprint import pprint

# Select the vSphere to be modified
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# Retrieve all distributed switches
dsw = vmw.list_dvswitch()

# Retrieve all portgroups.
pgdir = vmw.list_portgroups()

for pg in pgdir:
    pgdir[pg]['dvsname'] = dsw[pgdir[pg]['dvs']['name']]

pprint(pgdir)
