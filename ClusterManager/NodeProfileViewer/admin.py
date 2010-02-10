from ClusterManager.NodeProfileViewer.models import Node, ACme, ACmeBinding, Cluster
from django.contrib import admin

admin.site.register(Node)
admin.site.register(ACme)
admin.site.register(ACmeBinding)
admin.site.register(Cluster)