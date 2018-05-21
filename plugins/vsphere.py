'''
Created on May 3, 2018

@author: mkhan
'''
from plugins.baseplugin import BasePlugin

class VSphere(BasePlugin):
    '''
    classdocs
    '''


    def __init__(self, source, destination):
        '''
        Constructor
        '''
        self.name = "VSphere"
        self.type= "RemoteAPI"