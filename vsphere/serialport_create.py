#! /usr/bin/env python

from vsphere import vSphere
from vsphere import credentials

inputs = 'inputs/vsphere_myvmware.yml'


# Specify the telnet port
telnetport = raw_input("Telnet port: ")
while not telnetport.isdigit():
    telnetport = raw_input("Telnet port must be a number: ")


vm_name = raw_input("VM name: ")


# Create an instance of Class vSphere
cred = credentials(inputs)
vmw = vSphere(*cred)


# Check if VM exist

# Create serial port
vmw.add_telnet(vm_name, telnetport)



