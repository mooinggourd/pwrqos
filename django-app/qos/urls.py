from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'qos.views.home', name='home'),
    # url(r'^qos/', include('qos.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', 'services.views.index', name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^services/', include('services.urls', namespace='services')),        
    
)
