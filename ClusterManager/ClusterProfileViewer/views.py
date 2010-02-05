from django.http import HttpResponse
from django.template import Context, loader
from ClusterManager.ClusterProfileViewer.models import Cluster, ClusterMapping

def index(request):
    clusters = Cluster.objects.all()
    ret_str = ''
    for cluster in clusters:
        ret_str += 'Cluster ' + cluster.name + '\n'
        for node in cluster.get_nodes():
            ret_str += 'Node ' + node.name + '\n'
    t = loader.get_template('polls/index.html')
    c = Context({
        'latest_poll_list': latest_poll_list,
    })
    return HttpResponse(t.render(c))

    return HttpResponse(ret_str)