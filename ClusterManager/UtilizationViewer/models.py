from django.db import models

# Create your models here.
class Utilization(models.Model):
    ip = models.IPAddressField()
    # mac ?
    cpu_util = models.FloatField()
    mem = models.FloatField()
    num_proc = models.IntegerField()
    load = models.FloatField()
    power_usage = models.FloatField(db_index=True)
    # auto_now_add sets the ts to current timestamp everytime it is created
    ts = models.DateField(auto_now_add=True) 
    
    def __unicode__(self):
        return "Utilization for " + str(self.ip) + " at " + str(self.ts)
