from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from ClusterManager.NodeProfileViewer.models import Cluster
import json
import time
import sys
import traceback

def index(request):
    clusters = Cluster.objects.all()
    ret_val = []
    for cluster in clusters:
        final_power_data = ''
        final_util_data = ''
        counter = 1
        print "Cluster", cluster, cluster.get_nodes()
        for node in cluster.get_nodes():
            if counter != 1:
                final_power_data += ", "
                final_util_data += ", "
            counter += 1
            
            node_power_usage = {}
            node_power_usage['label'] = 'Power usage for ' + node.name
            power_data = []
            try:
                for power in node.get_power_usage():
                    t = time.mktime(power.ts.timetuple())
                    power_data.append([t*1000, power.power_usage])
            except:
                traceback.print_exc(file=sys.stdout)
                raise
            
            node_power_usage['data'] = power_data
            final_power_data += json.dumps(node_power_usage)
            
            # print node_power_usage['label'], node_power_usage
            
            node_utilization = {}
            node_utilization['label'] = 'Utilization for ' + node.name
            util_data = []
            try:
                for util in node.get_utilization():
                    t = time.mktime(util.ts.timetuple())
                    util_data.append([t*1000, util.cpu_util])
            except:
                traceback.print_exc(file=sys.stdout)
                raise
                
            node_utilization['data'] = util_data
            final_util_data += json.dumps(node_utilization)
            
        ret_val.append((cluster, final_power_data, final_util_data,))

    
    return render_to_response('index.html', {'cluster_data': ret_val})
