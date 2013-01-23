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
    def __init__(self, *args, **kwargs):
        self.services = kwargs.pop('services', [])        
        super(MeasurementWizardForm, self).__init__(*args, **kwargs)

        for i, s in enumerate(self.services):
            dom_id = 'id_service%d' % i
            label = mark_safe(u'<b>Metody usługi %s.</b><br/>' % s.name)
            self.fields['service%d' % i] = forms.ModelMultipleChoiceField(
                queryset=Method.objects.filter(service=s),
                label=label, 
                error_messages={'required': u'Wybierz co najmniej jedną metodę usługi %s.' % s.name},
                widget=forms.SelectMultiple(attrs = {'class': 'method_selection'}))

    def clean(self):
        cleaned_data = super(MeasurementWizardForm, self).clean()
        
        methods = []
        for k, v in self.cleaned_data.items():
            if k.startswith('service'):
                print v
                methods.extend(v)
        
        cleaned_data.update({'methods': methods})
        return cleaned_data

class MetricSelectionForm(MeasurementWizardForm):
    def __init__(self, *args, **kwargs):
        self.methods = kwargs.pop('methods', [])        
        super(MeasurementWizardForm, self).__init__(*args, **kwargs)

        for i, m in enumerate(self.methods):
            dom_id = 'id_method%d' % i
            label = mark_safe(u'<b>Metryki dla metody %s z usługi %s.</b><br/>' % (m.name, m.service.name))
            self.fields['method%d' % i] = forms.ModelMultipleChoiceField(
                queryset=Metric.objects.all(),
                initial= Metric.objects.all(),  
                label=label, 
                error_messages={'required': u'Wybierz co najmniej jedną metrykę.'},
                widget=forms.SelectMultiple(attrs = {'class': 'metric_selection'}))
