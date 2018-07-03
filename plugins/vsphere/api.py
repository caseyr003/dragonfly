'''
Modified July 3 2018

@author: caseyr003, alex wagstaff
'''
from pyVim.connect import SmartConnect, Disconnect
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL
import pyVmomi
import vsphere_utils


class VSphereAPI(object):
    """
    vSphere API Class
    """

    def __init__(self, host, user, password):
        '''
        Constructor
        '''
        self.name = "VSphere"
        self.type = "RemoteAPI"

        self.host = host
        self.user = user
        self.password = password

    def establish_connection(self):
        ssl = False
        if ssl:
            si = SmartConnect(host=self.host, user=self.user, pwd=self.password)
            print("Valid Certificate")
            return si

        else:
            si = SmartConnectNoSSL(host=self.host, user=self.user, pwd=self.password)
            print("Invalid or Untrusted Certificate")
            return si

    def enumerate(self):

        try:
            si = self.establish_connection()
            atexit.register(Disconnect, si)
            content = si.RetrieveContent()
            root_folder = content.rootFolder
            view_type = [vim.VirtualMachine]
            container_view = content.viewManager.CreateContainerView(root_folder, view_type,
                                                                 True)  # search recursively

            vms = container_view.view
            for vm in vms:
                summary = vm.summary
                print("Name: ", summary.config.name)
                print("Path: ", summary.config.vmPathName)
                print("Instance UUID: ", summary.config.instanceUuid)
                print("Bios UUID: ", summary.config.uuid)
                print("")  # add a new line between each VM printed

            return  # Return after enumerating the VMs
        except pyVmomi.VmomiSupport.InvalidLogin:
            print("The login information entered is invalid.")

    def export(self, uuid):
        try:
            si = self.establish_connection()
            service_content = si.RetrieveContent()
            atexit.register(Disconnect, si)
            vm = service_content.searchIndex.FindByUuid(None, uuid, True, True)

            if not vm:
                print("VM with the uuid {} was not found or does not exist.".format(uuid))
                return
            else:
                print("VM found.")

            cookie = si._stub.cookie
            cookie = vsphere_utils.process_cookie(cookie)
            print("the value of cookie is: ", cookie)

        except Exception as ex:
            print(ex.message)


def main():
    c = VSphereAPI("192.168.253.252", "administrator@vsphere.local", "Oracle:1234@")
    #c.enumerate()
    c.export("5002f189-47f8-809f-33aa-6bb6d64880fc")
    return 0


if __name__ == "__main__":
    main()


