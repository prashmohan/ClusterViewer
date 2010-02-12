from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from ClusterManager.NodeProfileViewer.models import Cluster
import json
import time
import datetime
import sys
import traceback



def index(request):
    clusters = Cluster.objects.all()
    ret_val = []
    for cluster in clusters:
        final_power_data = ''
        final_util_data = ''
        counter = 1
        for node in cluster.get_nodes():
            if counter != 1:
                final_power_data += ", "
                final_util_data += ", "
            counter += 1
            
            final_power_data += node.get_power_usage_json()
            final_util_data += node.get_utilization_json()
        
        ret_val.append((cluster, final_power_data, final_util_data,))
    
    
    return render_to_response('index.html', {'cluster_data': ret_val})
