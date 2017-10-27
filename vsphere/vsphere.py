import atexit
import ssl
from pyVim import connect
from pyVim.connect import Disconnect
from pyVmomi import vim, vmodl
import time
import yaml
import getpass
import sys, getopt



from os import listdir
from os.path import isfile, join


# Specify the common inventory folder
mypath = 'inputs'


def getiventories(mypath):
    """
    :param mypath: Path to inventory files
    :return:       List of local inventories - useful for help
    """
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    inv_list = []
    for file in onlyfiles:
        inv_list.append(file.split('_')[-1][:-4])
    return inv_list


def seldc(argv):
    """
    :param argv: Command line arguments
    :return:     Name of the inventory file
    """
    inp = ''
    try:
        opts, args = getopt.getopt(argv, "hi:")
    except getopt.GetoptError:
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print 'Use this script with inventory parameter'
            print(' -i myvmware - for MyVMware lab ')
            sys.exit()
        elif opt in ("-i"):
            if arg in getiventories(mypath):
                inp = arg
            else:
                print('Invalid argument')
                print('Only these inventories are valid: ', getiventories(mypath))
                sys.exit()
    if not(opts):
        print 'Use this script with the parameter e.g.:'
        print 'python <script>.py -i <DC>'
        print 'python <script>.py -h for more information'
        sys.exit()
    inp = mypath + '/vsphere_' + inp + '.yml'
    return inp


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
    dswitch['banner'] = vm_sw['banner']
    if 'actuplink' in vm_sw.keys():
        dswitch['actuplink'] = vm_sw['actuplink']

    return dswitch


class vSphere:

    def __init__(self, vsphere_ip, login, pswd):
        self.vsphere_ip = vsphere_ip
        self.login = login
        self.pswd = pswd



    def get_vm_id(self, content, vimtype, objid):
        """
        Get the VM associated with a given id - 'vim.VirtualMachine:vm-18'
        """
        recursive = True  # whether we should look into it recursively
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, recursive)
        for c in container.view:
            if c.summary.vm == objid:
                obj = c
                break
        return obj


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



    def get_all(self, content, vimtype):
        """
        Get the vsphere object associated with a given text name
        """
        recursive = True  # whether we should look into it recursively
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, recursive)
        return container.view



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
            print('The distributed port {0} group exists'.format(dvpgname))
            print(str(obj.summary.network)).replace('vim.dvs.DistributedVirtualPortgroup:', '')
            dupplicate = True
        else:
            print('Distributed Port Group not found')
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
                print('The VLAN {0} exists'.format(vlan))
                dupplicate = True
        if not dupplicate:
            print('VLAN ID not found')
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
            print out
            raise task.info.error

        return task.info.result



    def add_dvPort_group(self, dvswname, dv_port_name, vlan_id, *args):
        """
        It creates new distributed port group
        """
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
        # Configure active uplink ports
        if args:
            dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.inherited = False
            dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort = []
            for arg in args:
                dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort.append(arg)
                # dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort = actuplink
                # dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort[0] = actuplink[0]
                # dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.activeUplinkPort[1] = actuplink[1]
        else:
            dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.inherited = True

        #dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.standbyUplinkPort = 'Unset'
        #dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.standbyUplinkPort[0] = "dvUplink2"
        #dv_pg_spec.defaultPortConfig.uplinkTeamingPolicy.uplinkPortOrder.standbyUplinkPort[1] = "dvUplink4"

        dv_switch = self.find_dvSwitch(dvswname)

        task = dv_switch.AddDVPortgroup_Task([dv_pg_spec])
        self.wait_for_task(task)
        print("Successfully created DV Port Group {0}".format(dv_port_name))
        

    def list_portgroups(self):
        """
        It provides a directory of all portgroups, VLANs
        """
        dvportgroups = {}
        content = self.retrieve_content()
        obj = self.get_all(content, [vim.dvs.DistributedVirtualPortgroup])

        for i in obj:
            dvs_id = str(i.config.distributedVirtualSwitch).split(':')[-1][:-1]
            name = i.summary.name
            id = str(i.summary.network).split(':')[-1][:-1]
            try:
                vlan = i.config.defaultPortConfig.vlan.vlanId
                # vlan-id is referred to data type integer
                # vlan-range is referred to data type class 'pyVmomi.VmomiSupport.vim.NumericRange[]'
                if type(vlan) != int:
                    vlan = 'NumericRange'
            except:
                vlan = 'N/A'
            try:
                pvlan = i.config.defaultPortConfig.vlan.pvlanId
            except:
                pvlan = 'N/A'

            dvportgroups[name] = {'id': id, 'vlan': vlan, 'pvlan': pvlan, 'dvs_id': dvs_id}

        return dvportgroups



    def list_dvswitch(self):
        """
        It searches for all distributed switches
        """
        dswitch = {}
        content = self.retrieve_content()
        obj = self.get_all(content, [vim.DistributedVirtualSwitch])

        for i in obj:
            dvs = str(i).split(':')[-1][:-1]
            """
            pg_list = []
            for j in range(len(i.summary.portgroupName)):
                pg_list.append(i.summary.portgroupName[j])
            """
            dswitch[dvs] = {'name': i.summary.name, 'uuid': i.summary.uuid}

        return dswitch





    def del_dvPort_group(self, dv_port_name):
        # Deletes specific virtual portgroup
        content = self.retrieve_content()
        obj = self.get_obj(content, [vim.DistributedVirtualPortgroup], dv_port_name)
        if obj:
            task = obj.Destroy_Task()
            self.wait_for_task(task)
        else:
            print("The specified distributed port group doesn't exist")



    def find_vm(self, vmname):
        """
        It searches for specific VM
        """
        content = self.retrieve_content()
        obj = self.get_obj(content, [vim.VirtualMachine], vmname)
        return obj



    def add_telnet(self, vmname, port):
        serial_spec = vim.vm.device.VirtualDeviceSpec()
        serial_spec.operation = 'add'
        serial_port = vim.vm.device.VirtualSerialPort()
        serial_port.yieldOnPoll = True

        backing = serial_port.URIBackingInfo()
        backing.serviceURI = 'telnet://:' + port
        backing.direction = 'server'
        serial_port.backing = backing
        serial_spec.device = serial_port

        dev_changes = []
        dev_changes.append(serial_spec)

        # load empty config template applicable to VMs
        spec = vim.vm.ConfigSpec()
        spec.deviceChange = dev_changes

        vm = self.find_vm(vmname)
        task = vm.ReconfigVM_Task(spec)
        self.wait_for_task(task)


    def list_vm(self):
        """
        It searches for all VMs
        """
        content = self.retrieve_content()
        obj = self.get_all(content, [vim.VirtualMachine])
        vmdir = {}

        for i in obj:
            vmdir[i.summary.config.name] = {'vm-id': str(i).split(':')[-1][:-1], 'uuid': i.summary.config.uuid,
                                            'hostname': i.summary.guest.hostName, 'ip': i.summary.guest.ipAddress}


        return vmdir

