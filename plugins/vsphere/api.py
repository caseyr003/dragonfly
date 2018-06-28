'''
updated on June 28, 2018

@author: caseyr003, alex wagstaff
'''
from pyVim.connect import SmartConnect, Disconnect
import atexit
from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL
import pyVmomi
import threading
import time


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

    @staticmethod
    def process_cookie(cookie):
        """Split the cookie used for exporting into its component parts. return a dictionary of cookie name and value"""
        print("The cookie information is: ", cookie)
        cookie_name = cookie.split("=", 1)[0]
        cookie_value = cookie.split("=", 1)[1].split(";", 1)[0]
        cookie_path = cookie.split("=", 1)[1].split(";", 1)[1].split(
            ";", 1)[0].lstrip()
        cookie_body = " " + cookie_value + "; $" + cookie_path
        cookie_dict = dict()
        cookie_dict[cookie_name] = cookie_body

        return cookie_dict

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
            #TODO: create a persistent connection object. Close connection on program close.
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

    def export(self):
        try:
            si = self.establish_connection()
            atexit.register(Disconnect, si)
            cookie = si._stub.cookie
            cookie = self.process_cookie(cookie)
            print("the value of cookie is: ", cookie)

        except Exception as ex:
            print(ex.message)
            return

    class ProgressUpdater(threading.Thread):
        def __init__(self, vm_lease, update_time):
            super().__init__(self)
            self.vm_lease = vm_lease
            self.update_time = update_time
            self.progress_percent = 0

        def set_progress_percent(self, progress_percent):
            self.progress_percent = progress_percent

        def run(self):
            while True:
                try:
                    if self.vm_lease.state == vim.HttpNfcLease.State.done:
                        return
                    print("Progress of lease updating to ", self.progress_percent)
                    self.vm_lease.HttpNfcLeaseProgress(self.progress_percent)
                    time.sleep(self.update_time)
                except Exception as ex:
                    print(ex.message)
                    return


def main():
    c = VSphereAPI("192.168.253.252", "administrator@vsphere.local", "Oracle:1234@")
    c.export()
    return 0

#TODO: Remove main for testing when function is completed
if __name__ == "__main__":
    main()
