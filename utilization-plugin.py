#!/usr/bin/env python
# encoding: utf-8

import os
import logging
import traceback
import sys

from Gmetad.gmetad_plugin import GmetadPlugin
from Gmetad.gmetad_config import getConfig, GmetadConfig

def get_plugin():
    ''' All plugins are required to implement this method.  It is used as the factory
        function that instanciates a new plugin instance. '''
    # The plugin configuration ID that is passed in must match the section name 
    #  in the configuration file.
    return MySQLLogger('mysqllogger')

class MySQLLogger(GmetadPlugin):
    ''' This class implements the RRD plugin that stores metric data to RRD files.'''
    
    def __init__(self, cfgid):
        try:
            # The call to the parent class __init__ must be last
            GmetadPlugin.__init__(self, cfgid)
            logging.debug ("Starting cluster state server")
        except:
            print "Error in init"
            traceback.print_exc(file=sys.stdout)
            raise
            
        print 'Finished init'
        
    # def _parseConfig(self, cfgdata):
    #     '''This method overrides the plugin base class method.  It is used to
    #         parse the plugin specific configuration directives.'''
    #     for kw,args in cfgdata:
    #         if self.kwHandlers.has_key(kw):
    #             self.kwHandlers[kw](args)

    def start(self):
        '''Called by the engine during initialization to get the plugin going.'''
        pass
    
    def stop(self):
        '''Called by the engine during shutdown to allow the plugin to shutdown.'''        
        pass

    def notify(self, clusterNode):
        '''Called by the engine when the internal data source has changed.'''
        self._populateState(clusterNode)
        
    def _populateState(self, clusterNode):
        # clusterState [clusterName] [hostName] [metricName] = [val, sum, num]
        print "Cluster: ", str(clusterNode.getAttr('name'))
        
        for hostNode in clusterNode:
            hostName = str(hostNode.getAttr('name'))
            print '------------------------------------'
            print hostName

            print "Last Reported: ", int(hostNode.getAttr('reported'))
            print "IP: ", str(hostNode.getAttr('ip'))
            print dir(hostNode)
            # Update metrics for each host
            for metricNode in hostNode:
                metricName = str(metricNode.getAttr('name'))
                print metricName, str(metricNode.getAttr('val'))
            print ''
                
                
if __name__ == '__main__':
    print "This is not a stand alone program. This should be executed only as part of the python gmetad program as a plugin!"
    sys.exit(1)
