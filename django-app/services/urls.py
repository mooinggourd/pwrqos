from django.conf.urls import patterns, url
from services import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^measurements/service/(?P<service>\d+)/$',
        views.MeasurementsList.as_view(),
        name='measurements'),    

    url(r'^plot/service/(?P<service>\d+)/$',
        views.MeasurementsPlotView.as_view(),
        name='plots'),    
    
    url(r'^(?P<service_id>\d+)/$', views.details, name='details'),
    url(r'^measure/$', views.MeasurementWizard.as_view(views.MeasurementWizard.FORMS),
        name='measurement_wizard'),
        
    url(r'^ajax/measure/$', views.run_text_ajax, name='ajax_measure'),
)
