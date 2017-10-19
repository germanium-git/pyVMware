#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import dvswitch


inputs = 'inputs/vsphere.yml'

# It returns the name of distributed switch and active uplink in teaming policy
dswitch = dvswitch(inputs)

print(dswitch['actuplink'])


# Specify manually the distributed port group to be created
dportgroup = raw_input("Distributed port group: ")
vlanid = ''
while not vlanid.isdigit():
    vlanid = raw_input("VLAN-ID: ")



# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)


# Check if the port group already exist and the VLAN is not assigned to other port groups
if not (vmw.find_dvportgroup(dportgroup) or vmw.find_vlan(dswitch['name'], vlanid)):
    # Create port group
    vmw.add_dvPort_group(dswitch['name'], dportgroup, vlanid, dswitch['actuplink'])
else:
    print("\nDistributed port group can't be created")

