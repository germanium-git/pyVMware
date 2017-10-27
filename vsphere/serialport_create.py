#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials
from vsphere import seldc
import sys
from termcolor import cprint

# Select the vSphere to be modified
inputs = seldc(sys.argv[1:])


# Specify the telnet port
telnetport = raw_input("Telnet port: ")
while not telnetport.isdigit():
    telnetport = raw_input("Telnet port must be a number: ")


vm_name = raw_input("VM name: ")


# Review and accept or decline the proposed changes
cprint('\nReview the serial port to be created:', 'red')
print('  Telnet port: %s ' % telnetport)
print('  VM:          %s ' % vm_name)

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
    if vmw.find_vm(vm_name):
        vmw.add_telnet(vm_name, telnetport)
    else:
        print('VM {} not found'.format(vm_name))




