'''
Created on May 3, 2018

@author: mkhan
'''

from plugins.baseplugin import BasePlugin
from plugins.ocic.api import ComputeAPI


class OCIC(BasePlugin):
    '''
    classdocs
    '''
    def __init__(self, tenant, username, password, api_host):
        '''
        Constructor
        '''
        self.tenant = tenant
        self.username = username
        self.password = password
        self.api_host = api_host
        self.name = "OCIC"
        self.api = None

    def authenticate(self):
        success = False
        api = ComputeAPI(self.tenant, self.username, self.password, self.api_host)
        status = api.authenticate()
        if status == "Success":
            success = True
            self.api = api
        return [success, status]

    def list(self):
        instances = self.api.list_instances()
        data = []
        for instance in instances:
            data.append(instance["label"])

        return data

    def transfer(self):
        pass
