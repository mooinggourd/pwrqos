#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.utils.safestring import mark_safe

from services.models import Service, Method, Metric
from services import misc

class MeasurementWizardForm(forms.Form):
    def process_previous_data(self, data):
        pass

class ServiceSelectionForm(MeasurementWizardForm):
    services = misc.ServiceMultipleModelChoiceField(queryset=Service.objects.all(),
        widget=misc.ColumnCheckboxSelectMultiple(css_class='service-list'),
        label='',
        error_messages={'required': 'Wybierz co najmniej jedną usługę.'})

class MethodSelectionForm(MeasurementWizardForm):
    methods = forms.ModelMultipleChoiceField(queryset=Method.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='',
        error_messages={'required': 'Wybierz co najmniej jedną metodę.'})

    def __init__(self, *args, **kwargs):
        services = kwargs.pop('services', [])        
        super(MeasurementWizardForm, self).__init__(*args, **kwargs)
        
        self.fields['methods'] = forms.ModelMultipleChoiceField(queryset=Method.objects.filter(service__in=services),
            widget=forms.CheckboxSelectMultiple,
            label='',
            error_messages={'required': 'Wybierz co najmniej jedną metodę.'})

    def process_previous_data(self, data):
        service_ids = data.get('service_selection-services', [])
        self.fields['methods'].queryset = Method.objects.filter(service__in = service_ids)

class MetricSelectionForm(MeasurementWizardForm):

    def __init__(self, *args, **kwargs):
        self.methods = kwargs.pop('methods', [])        
        super(MeasurementWizardForm, self).__init__(*args, **kwargs)

        for i, m in enumerate(self.methods):
            dom_id = 'id_method%d' % i
            label = mark_safe(u'Metryki dla metody %s z usługi %s.<br/>' % (m.name, m.service.name))
            self.fields['method%d' % i] = forms.ModelMultipleChoiceField(
                queryset=Metric.objects.all(), 
                label=label, 
                error_messages={'required': 'Wybierz co najmniej jedną metrykę.'},
                widget=forms.SelectMultiple(attrs = {'class': 'metric_selection'}))
