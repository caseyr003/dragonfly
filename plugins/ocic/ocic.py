'''
Created on May 3, 2018

@author: mkhan
'''

from plugins.baseplugin import BasePlugin
from plugins.ocic.api import ClassicAPI


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
        # Authenticate through OCIC with the given credentials
        # obj being the return object. In this method it can be None.
        # rc is return code.
        # rc code structure
        #   0 - Success
        #   1 - General Failure
        #   2 - Authentication error
        #   3 - Socket error
        #   4 - Connected but timeout error
        # status_msg is the message which we send to flask app. or for debug purposes
        # We may not use all of the return variables in a method.
        # But following a common pattern around the project is better.
        api = ClassicAPI(self.tenant, self.username, self.password, self.api_host)
        session, code, status_msg = api.authenticate()
        if code == 0:
            self.api = api

        return code, status_msg

    def list(self):
        # returns a list of instances with their details.
        # obj represents the object with instance details in the following manner
        # obj = { {'name': 'instance1', 'size' = '', } , {'name': 'instance2', 'size':''}   }
        # rc = 0 - Success
        #       1 - General Failure
        #       3 - Socket error
        #       4 - Connection timeout error
        # Set API if none exists
        if self.api == None:
            code, status_msg = self.authenticate()
        if code != 0:
            return code, status_msg, []

        code, instances = self.api.list_instances()
        data = []
        if code == 0:
            for instance in instances:
                details = {'name': instance["label"], 'id': instance["name"]}
                data.append(details)

        return code, "Instance list retrieved successfully", data

    def transfer(self):
        pass
