from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from ClusterManager.NodeProfileViewer.models import Node, ACme, ACmeBinding
import json
import datetime
import time

def get_node_acme_mapping():
    bindings = ACmeBinding.objects.all()
    values = {}
    values['bindings'] = []
    for binding in bindings:
        values.append({'Name': binding.nodename, 'MAC': binding.mac, 'ACme ID': binding.acme.acme_id})
    
    return values
    
def get_node_acme_mapping_json(request):
    values = get_node_acme_mapping()
    return HttpResponse(json.dumps(values))

def get_node_acme_mapping_xml(request):
    values = get_node_acme_mapping()
    header = "<bindings>"
    tail = "</bindings>"
    ret_str = header
    for binding in values['bindings']:
        ret_str += "<node "
        ret_str += " name=\"" + binding['Name'] + "\""
        ret_str += " mac=\"" + binding['MAC'] + "\""
        ret_str += " acme_id=\"" + binding['ACme ID'] + "\""
        ret_str += "/>\n"
    return HttpResponse(ret_str)

def get_node_profile(request, node_id):
    pass
    
def get_node_power_usage(request, node_id):
    nodes = Node.objects.filter(node_id=node_id)
    if len(nodes) != 1:
        print 'Oh oh error.', nodes
    node = nodes[0]
    
    power_usage = node.get_power_usage()
    ret_val = {}
    ret_val['label'] = 'Power usage for ' + node.name
    data = []
    counter = 1
    for power in power_usage:
        t = time.mktime(power.ts.timetuple())
        data.append([t, power.power_usage])
        counter += 1
    ret_val['data'] = data
    
    return render_to_response('simple_node_profile.html', {'json_data': json.dumps(ret_val), 'node': node})