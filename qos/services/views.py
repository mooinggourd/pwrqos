from django.http import HttpResponse, Http404
from django.shortcuts import render
from services.models import Service

def index(request):
    context = {
        'services': Service.objects.all(),
    }
    return render(request, 'services/index.html', context)

def details(request, service_id):
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        raise Http404

    # parse the WSDL service description
    try:
        service.process_wsdl()
    except Service.WSDLError:
        # TODO: add proper logging
        print 'Failed to parse WSDL description of service %d.' % service.pk
        pass

    context = {
        'service': Service.objects.get(pk=service_id),
    }
    return render(request, 'services/details.html', context)
