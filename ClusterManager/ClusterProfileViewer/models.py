from django.db import models
from ClusterManager.NodeProfileViewer.models import Node

# Create your models here.
class Cluster(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    def get_nodes(self):
        cms = ClusterMapping.objects.filter(cluster=self)
        return [cm.node for cm in cms]
    
class ClusterMapping(models.Model):
    cluster = models.ForeignKey(Cluster)
    node = models.ForeignKey(Node)