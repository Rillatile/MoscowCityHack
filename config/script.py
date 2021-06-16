from db.models import (
    CoordinateData,
    Metric,
    OrganizationData,
    Subway
)


subway_metric = Metric.objects.get_or_create(name='метро', optim_config=True, generalizing_oper='sum')[0]
organization_metric = Metric.objects.get_or_create(name='конкуренты', optim_config=False, generalizing_oper='sum')[0]

organizations = OrganizationData.objects.all()
subways = Subway.objects.all()

for subway in subways:
    CoordinateData.objects.get_or_create(lon=subway.lon, lat=subway.lat, processed_value=1, metric=subway_metric)

for organization in organizations:
    CoordinateData.objects.get_or_create(lon=organization.lon, lat=organization.lat, processed_value=1, metric=organization_metric, activity=organization.type)
