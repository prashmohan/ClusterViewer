from django.db import models
from django.contrib.auth.models import User
import fields
import traceback
import time
import json
import sys
import datetime

FLOT_SCALING_FACTOR = 1000
UTIL_INTVL = 10
POWER_INTVL = 2
UTIL_TIMEOUT = 30
POWER_TIMEOUT = 5

def fill_data(ds, start, stop, intvl, fill_val, scale):
    for data in range(start, stop, intvl):
        ds.append([data * scale, fill_val])


# from ClusterManager.ClusterProfileViewer.models import Cluster

class Cluster(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)

    def __unicode__(self):
        return "Cluster " + self.name

    def get_nodes(self):
        return Node.objects.filter(cluster=self)

    def get_power_usage(self):
        nodes = self.get_nodes()
        return [node.get_power_usage() for node in nodes]

    def get_utilization(self):
        nodes = self.get_nodes()
        return [node.get_util_data() for node in nodes]

class NodeRegistration(models.Model):
    node = models.ForeignKey('Node')
    ip = models.IPAddressField()
    from_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.node
        
class Node(models.Model):
    node_id = models.IntegerField(db_index=True, primary_key=True, unique=True)
    name = models.CharField(max_length=30, unique=True)
    owner = models.ForeignKey(User, null=True)
    mac = fields.MACAddressField(unique=True, null=True)
    cluster = models.ForeignKey(Cluster, null=True)

    # Node PII
    # cpu_num = models.IntegerField(null=True)
    # cpu_speed = models.IntegerField(null=True)
    # machine_type = models.CharField(max_length=30, null=True)
    # os_release = models.CharField(max_length=30, null=True)
    # disk_total = models.FloatField(null=True)
    
    def __unicode__(self):
        return "Node (" + str(self.name) + ")"

    def get_power_usage(self):
        acme = ACmeBinding.objects.filter(node=self)
        if len(acme) != 1:
            # raise error
            print 'Error', acme
            return None
        acme = acme[0]
        last_hour = datetime.timedelta(minutes=2) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        return PowerUsage.objects.filter(node=acme).filter(ts__gte=last_time).order_by('ts')
        
    def get_utilization_json(self):
        node_utilization = {}
        node_utilization['label'] = 'Utilization for ' + self.name
        util_data = []
        prev_time = -1
        try:
            for util in self.get_utilization():
                t = time.mktime(util.ts.timetuple())
                if prev_time != -1 and (t - prev_time) > UTIL_TIMEOUT:
                    fill_data(util_data, prev_time + 10, t, 20, 0, FLOT_SCALING_FACTOR)
                util_data.append([t*FLOT_SCALING_FACTOR, util.cpu_util])
                prev_time = t
        except:
            traceback.print_exc(file=sys.stdout)
            raise
        
        if prev_time != -1 and time.mktime(datetime.datetime.now().timetuple()) - prev_time > 30:
            fill_data(util_data, prev_time + 10, time.mktime(datetime.datetime.now().timetuple()), 20, 0, 1000)
        
        node_utilization['data'] = util_data
        return json.dumps(node_utilization)
    
    # def get_power_usage_new(self, from_ts):
    #     acme = ACmeBinding.objects.filter(node=self)
    #     if len(acme) != 1:
    #         # raise error
    #         print 'Error', acme
    #         return None
    #     acme = acme[0]
    #     
    #     return ret_val
    
    def get_utilization(self):
        last_hour = datetime.timedelta(minutes=2) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        return Utilization.objects.filter(node=self).filter(ts__gte=last_time).order_by('ts')
        
    def get_power_usage_json(self):
        node_power_usage = {}
        node_power_usage['label'] = 'Power usage for ' + self.name
        power_data = []
        prev_time = -1
        try:
            for power in self.get_power_usage():
                t = time.mktime(power.ts.timetuple())
                if prev_time != -1 and (t - prev_time) > POWER_TIMEOUT:
                    fill_data(power_data, prev_time + 2, t, 2, 0, FLOT_SCALING_FACTOR)
                power_data.append([t*FLOT_SCALING_FACTOR, power.power_usage])
                prev_time = t
        except:
            traceback.print_exc(file=sys.stdout)
            raise
        if prev_time != -1 and time.mktime(datetime.datetime.now().timetuple()) - prev_time > 30:
            fill_data(power_data, prev_time + 2, time.mktime(datetime.datetime.now().timetuple()), 2, 0, 1000)
        
        node_power_usage['data'] = power_data
        return json.dumps(node_power_usage)        
                

class ACme(models.Model):
    acme_id = models.IntegerField(db_index=True)
    # acme_ip = models.IPAddressField(null=True)

    def __unicode__(self):
        return "ACme " + str(self.acme_id)

class ACmeBinding(models.Model):
    node = models.ForeignKey(Node)
    acme = models.ForeignKey(ACme)
    from_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.node) + ":" + str(self.acme)

class Utilization(models.Model):
    node = models.ForeignKey(Node)
    cpu_util = models.FloatField(null=True)
    mem = models.FloatField(null=True)
    proc_total = models.IntegerField(null=True)
    cpu_load = models.FloatField(null=True)
    # swap_free = models.IntegerField(null=True)

    # auto_now_add sets the ts to current timestamp everytime it is created
    ts = models.DateTimeField(auto_now_add=True) 

    def __unicode__(self):
        return "Utilization for " + str(self.ip) + " at " + str(self.ts)


class PowerUsage(models.Model):
    node = models.ForeignKey(ACme)
    power_usage = models.FloatField()
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __unicode__(self):
        return str(self.node) + ":" + str(self.power_usage) + ":" + str(self.ts)
        
