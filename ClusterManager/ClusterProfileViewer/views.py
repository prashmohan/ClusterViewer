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
        ret_val.append((cluster, cluster.get_power_usage_json(), cluster.get_utilization_json(),))
    
    
    return render_to_response('index.html', {'cluster_data': ret_val})
