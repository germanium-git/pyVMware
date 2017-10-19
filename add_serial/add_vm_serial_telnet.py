from pyVmomi import vim
from pyVim.connect import SmartConnect
from tools import tasks
import argparse
import getpass
import ssl


context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
context.verify_mode = ssl.CERT_NONE

def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to vCenter')

    # because -h is reserved for 'help' we use -s for service
    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='vSphere service to connect to')

    # because we want -p for password, we use -o for port
    parser.add_argument('-o', '--port',
                        type=int,
                        default=443,
                        action='store',
                        help='Port to connect on')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-d', '--datacenter',
                        required=False,
                        action='store',
                        help='Name of datacenter to search on')

    parser.add_argument('-n', '--name',
                        required=True,
                        action='store',
                        help='VM name')

    parser.add_argument('-t', '--telnetport',
                        required=False,
                        action='store',
                        help='telnet port to use when connecting to VM')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args


def get_dc(si, name):
    for dc in si.content.rootFolder.childEntity:
        if dc.name == name:
            return dc
    raise Exception('Failed to find datacenter named %s' % name)


def create_telnet_serial_port(value):
    serial_spec = vim.vm.device.VirtualDeviceSpec()
    serial_spec.operation = 'add'
    serial_port = vim.vm.device.VirtualSerialPort()
    serial_port.yieldOnPoll = True

    backing = serial_port.URIBackingInfo()
    backing.serviceURI = 'telnet://:' + value
    backing.direction = 'server'
    serial_port.backing = backing
    serial_spec.device = serial_port
    return serial_spec


def main():
    args = get_args()
    si = SmartConnect(host=args.host, user=args.user, pwd=args.password, sslContext=context,)
    if args.datacenter:
        dc = get_dc(si, args.datacenter)
    else:
        dc = si.content.rootFolder.childEntity[0]

    vm = si.content.searchIndex.FindChild(dc.vmFolder, args.name)
    if vm is None:
        raise Exception('Failed to find VM %s in datacenter %s' %
                        (dc.name, args.name))

    # configure new telnet serial port
    serial_spec = create_telnet_serial_port(args.telnetport)

    # apply configuration changes
    dev_changes = []
    dev_changes.append(serial_spec)

    # load empty config template applicable to VMs
    spec = vim.vm.ConfigSpec()
    spec.deviceChange = dev_changes
    task = vm.ReconfigVM_Task(spec=spec)
    tasks.wait_for_tasks(si, [task])


if __name__ == '__main__':
    main()
