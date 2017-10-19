import atexit
import ssl
from pyVim import connect
from pyVim.connect import Disconnect
from pyVmomi import vim, vmodl
import time
import yaml
import getpass



def credentials(inputfile):
    # Import credentials from YAML file
    with open(inputfile, 'r') as f:
        s = f.read()

    # Read the directory of credentials from file
    vm_cred = yaml.load(s)

    vsphere_ip = raw_input("vSphere IP [%s]: " % vm_cred['vsphere_ip']) or vm_cred['vsphere_ip']
    account = raw_input("Account [%s]: " % vm_cred['account']) or vm_cred['account']
    if 'passw' in vm_cred:
        passw = getpass.getpass(prompt='Use the stored password or enter new one: ', stream=None) or vm_cred['passw']
        passw = vm_cred['passw']
    else:
        passw = 'None'
        while passw == 'None' or passw == '':
            passw = getpass.getpass(prompt='Password: ', stream=None)

    return vsphere_ip, account, passw



def dvswitch(inputfile):
    # Import attributes specifying the distributed switch where distributed port groups are to be creted
    # Also the teaming policy - active uplink is read from YAML file
    with open(inputfile, 'r') as f:
        s = f.read()

    # Read the directory of credentials from file
    vm_sw = yaml.load(s)

    dswitch = {}
    dswitch['name'] = raw_input("Distributed switch [%s]: " % vm_sw['dswitch']) or vm_sw['dswitch']
    dswitch['actuplink'] = vm_sw['actuplink']

    return dswitch


class vSphere:

    def __init__(self, vsphere_ip, login, pswd):
        self.vsphere_ip = vsphere_ip
        self.login = login
        self.pswd = pswd


    def get_obj(self, content, vimtype, name):
        """
        Get the vsphere object associated with a given text name
        """
        recursive = True  # whether we should look into it recursively
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, recursive)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj


    def retrieve_content(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        si = None
        try:
            # print "Trying to connect to VCENTER SERVER . . ."
            si = connect.Connect(self.vsphere_ip, 443, self.login, self.pswd, sslContext=context)
            atexit.register(Disconnect, si)
        except IOError, e:
            pass
            # atexit.register(Disconnect, si)

        # print "Connected to VCENTER SERVER !"
        content = si.RetrieveContent()
        return content


    def find_dvportgroup(self, dvpgname):
        """
        It searches for specific distributed port-group on all distributed switches
        """

        content = self.retrieve_content()
        dupplicate = False
        obj = self.get_obj(content, [vim.DistributedVirtualPortgroup], dvpgname)
        # List all VLANs derfined for each distributed switch
        # print(obj.summary)
        # Check if object exists
        if obj and obj.summary.name == dvpgname:
            print('Attention - the distributed port {0} group already exists'.format(dvpgname))
            print(str(obj.summary.network)).replace('vim.dvs.DistributedVirtualPortgroup:', '')
            dupplicate = True
        else:
            print('No dupplicate Distributed Port Group found')
        return dupplicate


    def find_vlan(self, dwswname, vlan):
        """
        It searches for specific VLAN-ID on a specific distributed switch
        """
        content = self.retrieve_content()

        obj = self.get_obj(content, [vim.DistributedVirtualSwitch], dwswname)
        # print(obj.QueryUsedVlanIdInDvs())
        # List all VLANs derfined for each distributed switch
        dupplicate = False
        for i in obj.QueryUsedVlanIdInDvs():
            if i == int(vlan):
                print('Attention - the VLAN {0} already exists'.format(vlan))
                dupplicate = True
        if not dupplicate:
            print('No dupplicate VLAN ID found')
        return dupplicate

    def find_dvSwitch(self, dwswname):
        """
        It searches for specific VLAN-ID on a specific distributed switch
        """
        content = self.retrieve_content()
        obj = self.get_obj(content, [vim.DistributedVirtualSwitch], dwswname)
        return obj



    def wait_for_task(self, task, actionName='job', hideResult=False):
        """
        Waits and provides updates on a vSphere task
        """

        while task.info.state == vim.TaskInfo.State.running:
            time.sleep(2)
        if task.info.state == vim.TaskInfo.State.success:
            if task.info.result is not None and not hideResult:
                out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                print out
            else:
                out = '%s completed successfully.' % actionName
                print out
        else:
            out = '%s did not complete successfully: %s' % (actionName, task.info.error)
            raise task.info.error
            print out

        return task.info.result



    def add_dvPort_group(self, dvswname, dv_port_name, vlan_id, actuplink = 'Unset'):
        dv_pg_spec = vim.dvs.DistributedVirtualPortgroup.ConfigSpec()
        dv_pg_spec.name = dv_port_name
        dv_pg_spec.numPorts = 11
        dv_pg_spec.type = vim.dvs.DistributedVirtualPortgroup.PortgroupType.earlyBinding

        dv_pg_spec.defaultPortConfig = vim.dvs.VmwareDistributedVirtualSwitch.VmwarePortConfigPolicy()
        dv_pg_spec.defaultPortConfig.securityPolicy = vim.dvs.VmwareDistributedVirtualSwitch.SecurityPolicy()
        dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy = vim.dvs.VmwareDistributedVirtualSwitch.UplinkPortTeamingPolicy()
        dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder = vim.dvs.VmwareDistributedVirtualSwitch.UplinkPortOrderPolicy()

        # For port groups /w single VLAN
        dv_pg_spec.defaultPortConfig.vlan = vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec()
        dv_pg_spec.defaultPortConfig.vlan.vlanId = int(vlan_id)

        dv_pg_spec.defaultPortConfig.securityPolicy.allowPromiscuous = vim.BoolPolicy(value=False)
        dv_pg_spec.defaultPortConfig.securityPolicy.forgedTransmits = vim.BoolPolicy(value=True)

        dv_pg_spec.defaultPortConfig.vlan.inherited = False
        dv_pg_spec.defaultPortConfig.securityPolicy.macChanges = vim.BoolPolicy(value=True)
        dv_pg_spec.defaultPortConfig.securityPolicy.inherited = False

        # Specify teaming policy and name of the active uplink
        dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort = actuplink
        #dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.standbyUplinkPort = 'Unset'

        dv_switch = self.find_dvSwitch(dvswname)

        task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])
        self.wait_for_task(task)
        print("Successfully created DV Port Group {0}".format(dv_port_name))
        
  
    def del_dvPort_group(self, dv_port_name):
        # Deletes specific virtual portgroup
        content = self.retrieve_content()
        obj = self.get_obj(content, [vim.DistributedVirtualPortgroup], dv_port_name)
        if obj:
            task = obj.Destroy_Task()
            self.wait_for_task(task)
        else:
            print("The specified distributed port group doesn't exist")

