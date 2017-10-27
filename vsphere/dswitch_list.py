#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys

from pprint import pprint

# Select the vSphere to be modified
inputs = seldc(sys.argv[1:])


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)

# List of all distributed switches
dsw = vmw.list_dvswitch()

pprint(dsw)
