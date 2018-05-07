#! /usr/bin/env python

"""
===================================================================================================
   Author:          Petr Nemec
   Description:     Identify storage appliances dedicated for the NSX edge clusters
                    The clusters are identified by static 'NSX' string as a part of the name
                    It provides summary of all datastore appliances from all esx hosts
   Date:            2018-05-07
===================================================================================================
"""

from vsphere import Vsphere
from vsphere import credentials
from vsphere import seldc
import sys

# Select the vSphere instance
inputs = seldc(sys.argv[1:])

# Create an instance of Class vSphere
cred = credentials(inputs)
# Or bypass with custom credentials
# cred = ('10.20.30.40', 'administrator', 'mysecretpassword123')
vmw = Vsphere(*cred)

# Get a list of NSX-dedicated cluster; it searches for 'NSX' in the name of a cluster
clusters = vmw.list_clusters()

for cluster in clusters:
    print('\n')
    print(cluster)
    # Get a list of NSX-dedicated cluster; it searches for 'NSX' in the name
    datastores = vmw.find_cluster(cluster)['datastores']
    for i in range(len(datastores)):
        print(vmw.get_datastore_byid(datastores[i]), datastores[i])
