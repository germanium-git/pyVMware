#! /usr/bin/env python

"""
===================================================================================================
   Author:          Petr Nemec
   Description:     Identify storage appliances dedicated for the NSX edge clusters
                    The clusters are identified by static 'NSX' string as a part of the name
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

# Get a list of NSX-dedicated cluster; it searches for 'NSX' in the name
clusters = vmw.list_clusters()

# Retrieve all ESX hosts
hosts = vmw.list_hosts()

# Retrieve all datadstores
datastores = vmw.list_datastores()

# Identify subset of datastores attached to all hosts present in a cluster
for cluster in clusters:
    cluster_shared_storages = {}
    cluster_shared_storages['cluster_name'] = cluster
    cluster_shared_storages['cluster_id'] = clusters[cluster]['domain']
    current_host_storages = []
    next_host_storages = []
    hosts_in_cluster = len(clusters[cluster]['hosts'])
    # If there're more than one host in a cluster
    if hosts_in_cluster > 1:
        i = 0
        while i < (hosts_in_cluster - 1):
            current_host_storages = set(hosts[clusters[cluster]['hosts'][i]]['datastores'])
            next_host_storages = set(hosts[clusters[cluster]['hosts'][i+1]]['datastores'])
            common_storages = current_host_storages.intersection(next_host_storages)
            i += 1
            # print(common_storages)
    # If a cluster consists only one host
    else:
        common_storages = hosts[clusters[cluster]['hosts'][0]]['datastores']
    cluster_shared_storages['common_storages'] = list(common_storages)

    # Resolve the datastore-id to the name
    print('\n----------------------------------------------------')
    print(cluster_shared_storages['cluster_name'], cluster_shared_storages['cluster_id'])
    for i in range(len(cluster_shared_storages['common_storages'])):
        print(vmw.get_datastore_byid(cluster_shared_storages['common_storages'][i]),
              cluster_shared_storages['common_storages'][i])
