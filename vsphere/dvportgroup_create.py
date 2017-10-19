#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
from vsphere import dvswitch
import sys
from termcolor import cprint

# Select the vSphere to be modified
inputs = 'inputs/vsphere_' + seldc(sys.argv[1:]) + '.yml'

# Get the name of distributed switch, banner and active uplink in teaming policy
# specified in the inventory *.yml file
dswitch = dvswitch(inputs)


# Specify manually the distributed port group to be created
print('The distributed port group name following the pattern PODx_vlanid')
dportgroup = ''
while not dportgroup:
    dportgroup = raw_input("Distributed port group: ")
vlanid = ''
while not vlanid.isdigit():
    vlanid = raw_input("VLAN-ID: ")


# Display the information banner what vSphere instance is to be modified
print('\n')
cprint(dswitch['banner'], 'yellow')

# Review and accept or decline the proposed changes
cprint('\nReview the new distributed portgroup to be created:', 'red')
print('  Distributed switch: %s ' % dswitch['name'])
print('  VLAN-ID:            %s ' % vlanid)
if 'actuplink' in dswitch.keys():
    print('  Active uplinks:     %s ' % dswitch['actuplink'])
else:
    print("  Active uplink is not set - it'll be inherited from dvswitch")
print('\n')

agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Proceed with updating the configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Create an instance of Class vSphere
    cred = credentials(inputs)
    vmw = vSphere(*cred)

    # Check if the port group already exist and the VLAN is not assigned to other port groups
    if not (vmw.find_dvportgroup(dportgroup) or vmw.find_vlan(dswitch['name'], vlanid)):
        if 'actuplink' in dswitch.keys():
            print('\nCreating distributed port group')
            # Create port group with specific active uplinks
            vmw.add_dvPort_group(dswitch['name'], dportgroup, vlanid, *dswitch['actuplink'])
        else:
            # Create port group with the inherited teaming policy
            vmw.add_dvPort_group(dswitch['name'], dportgroup, vlanid)
    else:
        print("\nDistributed port group can't be created")

