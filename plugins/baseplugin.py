'''
Created on May 3, 2018

@author: mkhan
'''

import logging

class BasePlugin(object):
    '''
    stub class for migrator plugins
    '''

    def __init__(self, source, destination):
        '''
        Constructor
        source: location dict
        destination: location dict
        '''
        self.name = "BasePlugin"
        self.type = None # select from: LocalFile, RemoteAPI
    
    def enumerate(self):
        '''
        Return a list of migratable vms
        '''
        logging.debug("enumerate needs to be implemented for %s" % self.name)
    
    
    def transfer(self):
        '''
        Transfer vm to destination
        '''
        logging.debug("transfer needs to be implemented for %s" % self.name)