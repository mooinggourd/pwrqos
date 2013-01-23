#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
import suds

class Service(models.Model):    
    name = models.CharField(max_length=256, verbose_name='Nazwa')
    description = models.TextField(verbose_name='Opis')
    wsdl_url = models.URLField(verbose_name='Adres pliku WSDL')
    target_namespace = models.URLField(null=True, blank=True,
        verbose_name='URI docelowej przestrzeni nazw')
    internal_name = models.CharField(max_length=256, null=True, blank=True,
        verbose_name='Wewnętrzna nazwa')

    class Meta:
        verbose_name = u'Usługa'
        verbose_name_plural = u'Usługi'

    class WSDLError(Exception):
        pass

    def __unicode__(self):
        return self.name

    # TODO: przenieść do innej klasy, bo wsdl może mieć wiele usług
    def process_wsdl(self):
        if not self.wsdl_url:
            raise Service.WSDLError('WSDL\'s URL is missing.')
       
        try:
            client = suds.client.Client(self.wsdl_url)
        except:
            raise Service.WSDLError('Invalid WSDL file.')

        try:
            self.target_namespace = client.wsdl.tns[1]
        except:
            print 'target undef'
            raise Service.WSDLError('Target namespace is undefined.')

        for sd in client.sd:
            self.internal_name = sd.service.name
            for port in sd.ports:
                methods = port[1]
                for m in methods:
                    name, params = m
                    
                    kind, new = Kind.objects.get_or_create(name='unknown', 
                        namespace='unknown')
                    method, new = Method.objects.get_or_create(name=name, 
                        service=self, returned_kind=kind)
                    for pname, ptype in params:
                        kind, new = Kind.objects.get_or_create(name=ptype.type[0],
                                namespace=ptype.type[1])
                        param, new = MethodParam.objects.get_or_create(name=pname, 
                                kind=kind, method=method)
                        method.methodparam_set.add(param)

        self.save()            

class Kind(models.Model):
    namespace = models.URLField(null=True, verbose_name='URI przestrzeni nazw')
    name = models.CharField(max_length=256, verbose_name='Nazwa')

    class Meta:
        verbose_name = u'Typ wartości'
        verbose_name_plural = u'Typy wartości'

    def __unicode__(self):
        if self.namespace:
            return '%s:%s' % (self.namespace, self.name)
        else:
            return self.name

class Method(models.Model):
    name = models.CharField(max_length=256, verbose_name='Nazwa')
    returned_kind = models.ForeignKey(Kind, null=True, 
        verbose_name='Typ zwracanej wartości')
    service = models.ForeignKey(Service, verbose_name='Usługa')

    class Meta:
        verbose_name = u'Metoda'
        verbose_name_plural = u'Metody'

    def __unicode__(self):
        params = ', '.join(map(unicode, self.methodparam_set.all()))
        return '%s(%s): %s' % (self.name, params, self.returned_kind)

class MethodParam(models.Model):
    method = models.ForeignKey(Method, verbose_name='Metoda')
    name = models.CharField(max_length=128, verbose_name='Nazwa parametru')
    kind = models.ForeignKey(Kind, verbose_name='Typ wartości parametru')
    
    class Meta:
        verbose_name = u'Parametr metody'
        verbose_name_plural = u'Parametry metody'    
    
    def __unicode__(self):
        return self.name

class Metric(models.Model):
    name = models.CharField(max_length=256, verbose_name='Nazwa')
    description = models.TextField(verbose_name='Opis')
    method = models.ForeignKey(Method, verbose_name='Metoda')

    class Meta:
        verbose_name = u'Metryka'
        verbose_name_plural = u'Metryki'

    def __unicode__(self):
        if len(self.description) > 16:        
            short_desc = '%s...' % self.description[:64] 
        else:
            short_desc = self.description
        return '%s (%s)' % (self.name, short_desc)

class Measurement(models.Model):
    metric = models.ForeignKey(Metric, verbose_name='Metryka')
    time = models.DateTimeField(verbose_name='Czas wykonania')
    tested_method = models.ForeignKey(Method, verbose_name='Testowana metoda')
    
    class Meta:
        verbose_name = u'Pomiar'
        verbose_name_plural = u'Pomiary'    
    
    def __unicode__(self):
        return '%s (%s)' % (self.tested_method.name, 
            self.time.strftime('%Y-%m-%d %H:%M:%S'))

class Value(models.Model):
    value = models.TextField(verbose_name='Zmierzona wartość')
    kind = models.ForeignKey(Kind, verbose_name='Typ zmierzonej wartości')
    measurement = models.ForeignKey(Measurement, verbose_name='Pomiar')

    class Meta:
        verbose_name = u'Zmierzona wartość'
        verbose_name_plural = u'Zmierzone wartości'

    def __unicode__(self):
        return '%s: %s' % (self.value, self.kind.name)

