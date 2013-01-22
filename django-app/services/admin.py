from django.contrib import admin
from services.models import *

admin.site.register(Service)
admin.site.register(Method)
admin.site.register(Metric)
admin.site.register(Measurement)
admin.site.register(Value)
admin.site.register(Kind)
