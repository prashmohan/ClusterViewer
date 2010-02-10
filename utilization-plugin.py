#!/usr/bin/env python
# encoding: utf-8

import os
import logging
import traceback
import sys
import MySQLdb
import subprocess
import datetime
import time

from Gmetad.gmetad_plugin import GmetadPlugin
from Gmetad.gmetad_config import getConfig, GmetadConfig

def get_plugin():
    ''' All plugins are required to implement this method.  It is used as the factory
        function that instanciates a new plugin instance. '''
    # The plugin configuration ID that is passed in must match the section name 
    #  in the configuration file.
    return MySQLLogger('mysqllogger')

def get_node_id():
    """Get node ID"""
    # Hack! FIXME!
    proc = subprocess.Popen('/bin/hostname', stdout=subprocess.PIPE)
    proc.wait()
    host_name = proc.stdout.read().strip()
    return host_name[4:] # Gets worse and worse! Works only for Atom nodes
    
class MySQLLogger(GmetadPlugin):
    ''' This class implements the RRD plugin that stores metric data to RRD files.'''
    
    def __init__(self, cfgid):
        try:
            # The call to the parent class __init__ must be last
            GmetadPlugin.__init__(self, cfgid)
            logging.debug ("Starting cluster state server")
            self.conn = MySQLdb.connect(host='169.229.51.2', user='user', passwd='powerprofilecs262b', db='loclu')
            self.node_id = get_node_id()
            self.stmt_start = "INSERT INTO NodeProfileViewer_utilization (node_id"
        except:
            print "Error in init"
            traceback.print_exc(file=sys.stdout)
            raise


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
        logging.debug("Cluster: " + str(clusterNode.getAttr('name')))
        vals = self.node_id
        stmt = self.stmt_start
        
        for hostNode in clusterNode:
            hostName = str(hostNode.getAttr('name'))
            # Update metrics for each host
            for metricNode in hostNode:
                metricName = str(metricNode.getAttr('name'))
                # print metricName, str(metricNode.getAttr('val'))
                if metricName == 'cpu_idle':
                    stmt += ", cpu_util"
                    vals += ", " + str(100 - float(str(metricNode.getAttr('val'))))
                elif metricName == 'mem_free':
                    stmt += ", mem"
                    vals += ", " + str(metricNode.getAttr('val'))
                elif metricName == 'proc_total':
                    stmt += ", proc_total"
                    vals += ", " + str(metricNode.getAttr('val'))
                elif metricName == 'load_one':
                    stmt += ", cpu_load"
                    vals += ", " + str(metricNode.getAttr('val'))
        stmt += ", ts) VALUES ("
        vals += ", '" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "')"
        stmt += vals
        print stmt
        cursor = self.conn.cursor()
        cursor.execute(stmt)
        cursor.close()
                
                
if __name__ == '__main__':
    print "This is not a stand alone program. This should be executed only as part of the python gmetad program as a plugin!"
    sys.exit(1)
