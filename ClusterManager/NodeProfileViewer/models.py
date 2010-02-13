from django.db import models
from django.contrib.auth.models import User
import fields
import traceback
import time
import json
import sys
import datetime
from django.db.models import Sum
import logging

FLOT_SCALING_FACTOR = 1000
UTIL_INTVL = 10
POWER_INTVL = 2
UTIL_TIMEOUT = 30
POWER_TIMEOUT = 5
CLUSTER_GRAPH_TIME_FRAME = 10 # in minutes

def fill_data(ds, start, stop, intvl, fill_val, scale):
    for data in range(start, stop, intvl):
        ds.append([data * scale, fill_val])
        
def conv_pst(ts):
    return ts - (8 * 60 * 60)
    
def avg_data(ds):
    y = 0.0
    for entry in ds:
        y += entry[1]
    return y/len(ds)
        

class Cluster(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)

    def __unicode__(self):
        return "Cluster " + self.name
        
    def get_node_count(self):
        return Node.objects.filter(cluster=self).count()

    def get_nodes(self):
        return Node.objects.filter(cluster=self)

    def get_power_usage(self):
        # SELECT SUM(power) from Utilization where node_id in (SELECT node_id from Nodes where cluster_id=10) GROUP BY timestamp/10
        nodes = self.get_nodes()
        print nodes.count()
        last_hour = datetime.timedelta(minutes=CLUSTER_GRAPH_TIME_FRAME) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        power = PowerUsage.objects.filter(node__in=nodes).filter(ts__gte=last_time).values('ts').annotate(Sum('power_usage')).order_by('ts')
        return power


    def get_utilization(self):
        nodes = self.get_nodes()
        last_hour = datetime.timedelta(minutes=CLUSTER_GRAPH_TIME_FRAME) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        util = Utilization.objects.filter(node__in=nodes).filter(ts__gte=last_time).values('ts').annotate(Sum('cpu_util')).order_by('ts')
        return util

    def get_power_usage_json(self):
        cluster_power_usage = {}
        power_data = []
        prev_time = -1
        
        for power in self.get_power_usage():
            t = conv_pst(time.mktime(power['ts'].timetuple()))
            if prev_time != -1 and (t - prev_time) > POWER_TIMEOUT:
                fill_data(power_data, prev_time + 2, t, 2, 0, FLOT_SCALING_FACTOR)
            power_data.append([t*FLOT_SCALING_FACTOR, power['power_usage__sum']])
            prev_time = t
        if prev_time != -1 and conv_pst(time.mktime(datetime.datetime.now().timetuple())) - prev_time > 20 * POWER_TIMEOUT:
            fill_data(power_data, prev_time + 2, conv_pst(time.mktime(datetime.datetime.now().timetuple())) , 2, 0, FLOT_SCALING_FACTOR)
        
        cluster_power_usage['data'] = power_data
        cluster_power_usage['label'] = 'Power usage for ' + self.name # + ' = ' + str(avg_data(power_data))

        return json.dumps(cluster_power_usage)        
        
    def get_utilization_json(self):
        cluster_util = {}
        util_data = []
        prev_time = -1
        node_count = self.get_node_count()
        for util in self.get_utilization():
            t = conv_pst(time.mktime(util['ts'].timetuple()))
            if prev_time != -1 and (t - prev_time) > UTIL_TIMEOUT:
                fill_data(util_data, prev_time + 2, t, 2, 0, FLOT_SCALING_FACTOR)
            util_data.append([t*FLOT_SCALING_FACTOR, util['cpu_util__sum']/node_count])
            prev_time = t
        if prev_time != -1 and conv_pst(time.mktime(datetime.datetime.now().timetuple())) - prev_time > 20 * POWER_TIMEOUT: # 20* UTIL_TIMEOUT is too big to make sense
            fill_data(util_data, prev_time + 2, conv_pst(time.mktime(datetime.datetime.now().timetuple())) , 2, 0, FLOT_SCALING_FACTOR)
        
        cluster_util['data'] = util_data
        cluster_util['label'] = 'Utilization of ' + self.name

        return json.dumps(cluster_util)

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
    cluster = models.ForeignKey(Cluster, null=True, db_index=True)

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
        last_hour = datetime.timedelta(minutes=CLUSTER_GRAPH_TIME_FRAME) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        return PowerUsage.objects.filter(node=acme).filter(ts__gte=last_time).order_by('ts')
        
    def get_utilization_json(self):
        node_utilization = {}
        node_utilization['label'] = 'Utilization for ' + self.name
        util_data = []
        prev_time = -1
        for util in self.get_utilization():
            t = time.mktime(util.ts.timetuple())
            if prev_time != -1 and (t - prev_time) > UTIL_TIMEOUT:
                fill_data(util_data, prev_time + 10, t, 20, 0, FLOT_SCALING_FACTOR)
            util_data.append([t*FLOT_SCALING_FACTOR, util.cpu_util])
            prev_time = t
        
        if prev_time != -1 and time.mktime(datetime.datetime.now().timetuple()) - prev_time > 30:
            fill_data(util_data, prev_time + 10, time.mktime(datetime.datetime.now().timetuple()), 20, 0, 1000)
        
        node_utilization['data'] = util_data
        return json.dumps(node_utilization)
        
    def get_utilization(self):
        last_hour = datetime.timedelta(minutes=CLUSTER_GRAPH_TIME_FRAME) # last 1 hour
        last_time = datetime.datetime.now() - last_hour # time 1 hour before
        return Utilization.objects.filter(node=self).filter(ts__gte=last_time).order_by('ts')
        
    def get_power_usage_json(self):
        node_power_usage = {}
        node_power_usage['label'] = 'Power usage for ' + self.name
        power_data = []
        prev_time = -1
        for power in self.get_power_usage():
            t = time.mktime(power.ts.timetuple())
            if prev_time != -1 and (t - prev_time) > POWER_TIMEOUT:
                fill_data(power_data, prev_time + 2, t, 2, 0, FLOT_SCALING_FACTOR)
            power_data.append([t*FLOT_SCALING_FACTOR, power.power_usage])
            prev_time = t

        if prev_time != -1 and time.mktime(datetime.datetime.now().timetuple()) - prev_time > 30:
            fill_data(power_data, prev_time + 2, time.mktime(datetime.datetime.now().timetuple()), 2, 0, 1000)
        
        node_power_usage['data'] = power_data
        return json.dumps(node_power_usage)        
                

class ACme(models.Model):
    acme_id = models.IntegerField(db_index=True)

    def __unicode__(self):
        return "ACme " + str(self.acme_id)

class ACmeBinding(models.Model):
    node = models.ForeignKey(Node)
    acme = models.ForeignKey(ACme)
    from_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.node) + ":" + str(self.acme)

class Utilization(models.Model):
    node = models.ForeignKey(Node, db_index=True)
    cpu_util = models.FloatField(null=True)
    mem = models.FloatField(null=True)
    proc_total = models.IntegerField(null=True)
    cpu_load = models.FloatField(null=True)
    # swap_free = models.IntegerField(null=True)

    # auto_now_add sets the ts to current timestamp everytime it is created
    ts = models.DateTimeField(auto_now_add=True, db_index=True) 

    def __unicode__(self):
        return "Utilization for " + str(self.ip) + " at " + str(self.ts)


class PowerUsage(models.Model):
    node = models.ForeignKey(ACme, db_index=True)
    power_usage = models.FloatField()
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    
    def __unicode__(self):
        return str(self.node) + ":" + str(self.power_usage) + ":" + str(self.ts)
        
