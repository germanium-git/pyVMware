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


# Specify the telnet port
telnetport = raw_input("Telnet port: ")
while not telnetport.isdigit():
    telnetport = raw_input("Telnet port must be a number: ")


vm_name = raw_input("VM name: ")


# Display the information banner what vSphere instance is to be modified
print('\n')
cprint(dswitch['banner'], 'yellow')

# Review and accept or decline the proposed changes
cprint('\nReview the serial port to be created:', 'red')
print('  Telnet port: %s ' % telnetport)
print('  VM:            %s ' % vm_name)

agree = raw_input("Do you want to apply these changes? y/n[N]: " or 'N')


# Proceed with updating the configuration
if agree != "Y" and agree != "y":
    print("Script execution canceled")
    sys.exit(1)
else:
    # Create an instance of Class vSphere
    cred = credentials(inputs)
    vmw = vSphere(*cred)

    # Create serial port
    vmw.add_telnet(vm_name, telnetport)



