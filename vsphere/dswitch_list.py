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

# List all portgroups.
dsw = vmw.list_dvswitch()

for s in dsw:
    print('\n')
    print s
    print dsw[s]['uuid']
    for pg in dsw[s]['portgroups']:
        print pg
