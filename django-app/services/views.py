#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic import ListView, FormView
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from services.models import *

from django import forms
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime, time
from suds.client import Client
import json

import services.forms

# TODO: przenieść w lepsze miejsce
def run_test(method, metric):
    metric_mname = metric.method.name
    metric_wsdl = metric.method.service.wsdl_url

    method_wsdl = method.service.wsdl_url
    method_lname = method.name
    method_tns = method.service.target_namespace
    service_iname = method.service.internal_name
    
    try:
        c = Client(metric_wsdl)
        wrapper = getattr(c.service, metric_mname)  # może rzucić MethodNotFound
        result = wrapper(service_iname, method_wsdl, method_lname, method_tns)
        measurement = Measurement(metric=metric, 
            time=datetime.now(), tested_method=method)
        measurement.save()

        # TODO: wykrywanie typów zwracanych wartości
        try:          
            v = float(result)
            kind_name = 'float'
        except ValueError:
            try:                        
                v = int(result)
                kind_name = 'int'
            except ValueError:                    
                v = unicode(result)
                kind_name = 'string'
            
        kind, _ = Kind.objects.get_or_create(name=kind_name,
            namespace='http://www.w3.org/2001/XMLSchema')
        value = Value(value=v, kind=kind, measurement=measurement)
        value.save()
        
        return result            
    except:
        raise

@csrf_exempt
@require_http_methods(['POST'])
def run_text_ajax(request):
    try:
        method_pk = request.POST['method_pk']
        metric_pk = request.POST['metric_pk']
    except:
        return HttpResponse(status=400, content='Missing parameters.')
   
    method = get_object_or_404(Method, pk=method_pk)
    metric = get_object_or_404(Metric, pk=metric_pk)
                   
    result = run_test(method, metric)                   
    return HttpResponse(unicode(result))

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
 
class MeasurementsForm(forms.Form):
    method = forms.ModelMultipleChoiceField(queryset=Method.objects.all(),
        label='Metody')
    metric = forms.ModelMultipleChoiceField(queryset=Metric.objects.all(),
        label='Metryki')
    start = forms.DateField(required=False, label='Data początkowa')
    end = forms.DateField(required=False, label='Data końcowa')    
    page = forms.IntegerField(initial=0, widget=forms.HiddenInput())
    sort_by = forms.CharField(required=False, widget=forms.HiddenInput())    
    # TODO: dodać pola z datami od/do    
 
class MeasurementsList(FormView):
    template_name = 'services/result_archive.html'
    context_object_name = 'measurements'
    form_class = MeasurementsForm    
    
    sort_fields = {
        'value': 'value',
        'type': 'kind__name',
        'metric': 'measurement__metric__name',
        'method': 'measurement__tested_method__name',
        'date': 'measurement__time',
    }
    
    def get_form(self, form_class):
        form = super(FormView, self).get_form(form_class)
        service_id = self.kwargs['service']
        form.fields['method'].queryset = Method.objects.filter(service__pk=service_id)
        return form
            
    #def get(self, *args, **kwargs):
    #    result = super(FormView, self).get(*args, **kwargs)
    #    print 'get -> ', self.kwargs
    #    return result
    
    def form_valid(self, form):
        print self.kwargs
        context = self.get_context_data(form=form)
        context.update({'values': self.get_queryset(self.request.POST)})        
        return self.render_to_response(context)
    
    def get_queryset(self, post_params):
        try:
            method_ids = map(int, post_params.getlist('method'))
            metric_ids = map(int, post_params.getlist('metric'))
        except:
            raise Http404()
        
        queryset = Measurement.objects.all()

        queryset = queryset.filter(tested_method__pk__in=method_ids) \
            .filter(metric__pk__in=metric_ids)
            
        result = Value.objects.filter(measurement__in=queryset)
        
        sort_by = post_params.get('sort_by')
        if sort_by:
            if sort_by[0] == '-':        
                key = '-'
                sort_by = sort_by[1:]
            else:
                key = ''
        
            if sort_by in self.sort_fields:                
                result = result.order_by(key + self.sort_fields[sort_by])
        
        start_raw = post_params.get('start')
        if start_raw:
            try:
                start = datetime.strptime(start_raw, '%d.%m.%Y')
                result = result.filter(measurement__time__gte=start)
            except ValueError:
                pass
                
        end_raw = post_params.get('end')
        if end_raw:
            try:
                end = datetime.combine(datetime.strptime(end_raw, '%d.%m.%Y').date(),
                    time.max)
                result = result.filter(measurement__time__lte=end)
            except ValueError:
                pass
        
        paginator = Paginator(result, 15)        
        page_num = post_params.get('page', 1)
        try:        
            page = paginator.page(page_num)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)
        return page
    
class MeasurementWizard(SessionWizardView):
    FORMS = [
        ('service_selection', services.forms.ServiceSelectionForm),
        ('method_selection', services.forms.MethodSelectionForm),
        ('metric_selection', services.forms.MetricSelectionForm),
    ]
    TEMPLATES = {
        "service_selection": "services/measure_wizard/service_selection.html",
        "method_selection": "services/measure_wizard/method_selection.html",
        "metric_selection": "services/measure_wizard/metric_selection.html",
    }
    NAMES = [
        ('service_selection', 'Wybór usługi'),
        ('method_selection', 'Wybór metod'),
        ('metric_selection', 'Wybór metryk'),
        ('results', 'Raport'),
    ]
        
    def __init__(self, *args, **kwargs):
        super(SessionWizardView, self).__init__(*args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
   
    def get_context_data(self, form, **kwargs):
        context = super(SessionWizardView, self).get_context_data(form=form, **kwargs)
        context.update({'step_names': self.NAMES})
        
        if self.steps.current == 'metric_selection':
            method_data = self.get_cleaned_data_for_step('method_selection')
            context.update({
                'methods': method_data['methods'],
                'metrics': Metric.objects.all(),
            })            
        return context
        
    def process_step(self, form):
        data = self.get_form_step_data(form)

        cur_step = self.get_step_index()
        
        if cur_step == 0:
            cur_services = data.getlist('service_selection-services')
            stored_data =  self.storage.data['step_data'].get('service_selection', {})
            last_services = stored_data.get('service_selection-services', [])
            
            if set(cur_services) != set(last_services):
                self.storage.reset()
        return data
        
    def get_form_kwargs(self, step=None):    
        kwargs = super(SessionWizardView, self).get_form_kwargs(step)
        if step == 'method_selection':
            prev_data = self.get_cleaned_data_for_step('service_selection')
            kwargs.update({'services': prev_data['services']})
        elif step == 'metric_selection':
            prev_data = self.get_cleaned_data_for_step('method_selection')
            kwargs.update({'methods': prev_data['methods']})                        
        return kwargs
          
    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        methods = data.get('methods', [])

        ajax_data = []
        
        metric_selections = {
            # service: { method: [metrics] }
        }
                       
        for i, method in enumerate(methods):
            key = 'method%d' % i
            metrics = data.get(key, [])

            ajax_data.append([method.pk, list(metrics.values_list('pk', flat=True))])
            if method.service not in metric_selections:
                metric_selections[method.service] = {}
            
            metric_selections[method.service][method] = metrics

        context = {
            'services': metric_selections,
            'ajax_data': json.dumps(ajax_data),
        }
        return render(self.request, 'services/measure_wizard/results.html', context)

