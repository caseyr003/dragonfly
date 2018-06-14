'''
Created on June 14, 2018

@author: caseyr003
'''
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL
import pyVmomi


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
