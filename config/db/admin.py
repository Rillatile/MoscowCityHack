from django.contrib import admin

from .models import Activity, Scope, Layer, CoordinateData, Metric, BarLayers, SupermarketLayers, BakeryLayers, \
    BarbershopLayers, BeautySaloonLayers, CafeLayers, СosmeticsStoreLayers, HouseChemicLayers, DentistryLayers, \
    ClinicLayers

# Register your models here.0
admin.site.register(Activity)
admin.site.register(Scope)
admin.site.register(Layer)
admin.site.register(CoordinateData)
admin.site.register(Metric)
admin.site.register(SupermarketLayers)
admin.site.register(BakeryLayers)
admin.site.register(BarbershopLayers)
admin.site.register(BeautySaloonLayers)
admin.site.register(CafeLayers)
admin.site.register(BarLayers)
admin.site.register(СosmeticsStoreLayers)
admin.site.register(HouseChemicLayers)
admin.site.register(DentistryLayers)
admin.site.register(ClinicLayers)
