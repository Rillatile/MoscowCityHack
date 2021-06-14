from django.contrib import admin

from .models import Activity, Scope, Layer, CoordinateData, Metric, BarLayers

# Register your models here.0
admin.site.register(Activity)
admin.site.register(Scope)
admin.site.register(Layer)
admin.site.register(CoordinateData)
admin.site.register(Metric)
admin.site.register(BarLayers)
