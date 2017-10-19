#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
from vsphere import dvswitch
import sys
from termcolor import cprint

# Read the credentials for vSphere from YAML file and input dialog
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'

# It returns the name of distributed switch, banner and active uplink in teaming policy
dswitch = dvswitch(inputs)


dportgroup = raw_input("Distributed port group to be deleted: ")

cred = credentials(inputs)
vmw = vSphere(*cred)

# Check if the port group exist
if not vmw.find_dvportgroup(dportgroup):
    sys.exit()
else:
    print('\n')
    cprint(dswitch['banner'], 'yellow')
    cprint('\nReview the portgroup to be deleted:', 'red')
    print('  ' + dportgroup)
    print('\n')

    agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


    # Proceed with updating configuration
    if agree != "Y" and agree != "y":
        print("Script execution canceled")
        sys.exit(1)
    else:
        # Delete port group
        vmw.del_dvPort_group(dportgroup)


