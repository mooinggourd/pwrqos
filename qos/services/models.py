from django.db import models
import suds

class Service(models.Model):    
    name = models.CharField(max_length=256)
    description = models.TextField()
    wsdl_url = models.URLField()

    class WSDLError(Exception):
        pass

    def __unicode__(self):
        return self.name

    def process_wsdl(self):
        if not self.wsdl_url:
            raise Service.WSDLError('WSDL\'s URL is missing.')
       
        try:
            client = suds.client.Client(self.wsdl_url)
        except:
            raise Service.WSDLError('Invalid WSDL file.')

        for sd in client.sd:
            for port in sd.ports:
                methods = port[1]
                for m in methods:
                    name, params = m
                    
                    kind, new = Kind.objects.get_or_create(name='unknown', namespace='unknown')
                    method, new = Method.objects.get_or_create(name=name, service=self, returned_kind=kind)
                    for pname, ptype in params:                                            
                        kind, new = Kind.objects.get_or_create(name=ptype.type[0],
                                namespace=ptype.type[1])
                        param, new = MethodParam.objects.get_or_create(name=pname, 
                                kind=kind, method=method)
                        method.methodparam_set.add(param)

class Kind(models.Model):
    namespace = models.URLField(null=True)
    name = models.CharField(max_length=256)

class Method(models.Model):
    name = models.CharField(max_length=256)
    returned_kind = models.ForeignKey(Kind, null=True)
    service = models.ForeignKey(Service)

class MethodParam(models.Model):
    method = models.ForeignKey(Method)
    name = models.CharField(max_length=128)
    kind = models.ForeignKey(Kind)

class Metric(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    method = models.ForeignKey(Method)

class Measurement(models.Model):
    metric = models.ForeignKey(Metric)
    time = models.DateTimeField()
    tested_method = models.ForeignKey(Method)

class Value(models.Model):
    value = models.TextField()
    kind = models.ForeignKey(Kind)
    measurement = models.ForeignKey(Measurement)

