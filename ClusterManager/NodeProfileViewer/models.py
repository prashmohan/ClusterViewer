from django.db import models
# from django.contrib.auth.models import User
import fields

class NodeRegistration(models.Model):
    node = models.ForeignKey('Node')
    ip = models.IPAddressField()
    from_ts = models.DateField(auto_now_add=True)
    
    def __unicode__(self):
        return self.node
        
class Node(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    # owner = models.ForeignKey(User, null=True)
    mac = fields.MACAddressField(unique=True)

    def __unicode__(self):
        return "Node (" + str(self.mac) + ") " + str(self.name) #+ \
#                " owned by " + str(self.owner)

class ACme(models.Model):
    acme_id = models.IntegerField(db_index=True)
    acme_ip = models.IPAddressField(null=True)

    def __unicode__(self):
        return "ACme " + str(self.acme_id)

class ACmeBinding(models.Model):
    node = models.ForeignKey(Node)
    acme = models.ForeignKey(ACme)
    from_ts = models.DateField(auto_now_add=True)

    def __unicode__(self):
        return str(self.node) + ":" + str(self.acme)