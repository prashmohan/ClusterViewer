from django.db import models
from django.contrib.auth.models import User
import fields

class NodeRegistration(models.Model):
    node = models.ForeignKey('Node')
    ip = models.IPAddressField()
    from_ts = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.node
        
class Node(models.Model):
    node_id = models.IntegerField(db_index=True, primary_key=True, unique=True)
    name = models.CharField(max_length=30, unique=True)
    owner = models.ForeignKey(User, unique=True, null=True)
    mac = fields.MACAddressField(unique=True, null=True)

    def __unicode__(self):
        return "Node (" + str(self.name) + ")"

    def get_power_usage(self):
        acme = ACmeBinding.objects.filter(node=self)
        if len(acme) != 1:
            # raise error
            print 'Error', acme
            return None
        acme = acme[0]
        
        return PowerUsage.objects.filter(node=acme).order_by('-ts')[:10]
    
    def get_power_usage_new(self, from_ts):
        acme = ACmeBinding.objects.filter(node=self)
        if len(acme) != 1:
            # raise error
            print 'Error', acme
            return None
        acme = acme[0]
        
        return PowerUsage.objects.filter(node=acme).filter(ts__gte=from_ts).order_by('-ts')
                

class ACme(models.Model):
    acme_id = models.IntegerField(db_index=True)
    acme_ip = models.IPAddressField(null=True)

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
    num_proc = models.IntegerField(null=True)
    load = models.FloatField(null=True)

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
        


