from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from ClusterManager.ClusterProfileViewer.models import Cluster, ClusterMapping

def index(request):
    clusters = Cluster.objects.all()
    ret_str = ''
    for cluster in clusters:
        ret_str += 'Cluster ' + cluster.name + '\n'
        for node in cluster.get_nodes():
            ret_str += 'Node ' + node.name + '\n'
    return render_to_response('index.html',{'clusters': clusters})
