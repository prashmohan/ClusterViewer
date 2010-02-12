from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^ClusterManager/', include('ClusterManager.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    (r'^clusters/$', 'ClusterManager.ClusterProfileViewer.views.index'),
    (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/Users/prmohan/Projects/ClusterViewer/templates/'}),
    
    # ACme <--> Node mappings
    (r'^acme_mapping/$', 'ClusterManager.NodeProfileViewer.views.get_node_acme_mapping_json'),
    (r'^acme_mapping/json/$', 'ClusterManager.NodeProfileViewer.views.get_node_acme_mapping_json'),
    (r'^acme_mapping/xml/$', 'ClusterManager.NodeProfileViewer.views.get_node_acme_mapping_xml'),

    (r'^node/(?P<node_id>\d+)/$', 'ClusterManager.NodeProfileViewer.views.get_node_profile'),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
