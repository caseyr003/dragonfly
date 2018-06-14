'''
Created on May 3, 2018

@author: mkhan
'''
from plugins.baseplugin import BasePlugin
from plugins.vsphere.vsphere import VSphereAPI

class VSphere(BasePlugin):
    '''
    classdocs
    '''
    def __init__(self, host, user, password):
        '''
        Constructor
        '''
        self.name = "VSphere"
        self.type = "RemoteAPI"
        self.host = host
        self.user = user
        self.password = password

    def authenticate(self):
        pass

    def list(self):
        pass

    def transfer(self):
        pass
