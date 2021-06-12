from .models import (
    Activity,
    CoordinateData,
    OrganizationData
)


class CoordinateDataWrapper:
    def save(data):
        cd = CoordinateData(
            lat = data['lat'].replace(',', '.'),
            lon = data['lon'].replace(',', '.'),
            street = data['street'].lower(),
            house = data['house'].lower(),
            raw_values = data['raw_values'],
            processed_value = data['value']
        )

        cd.save()
    
    def all():
        return CoordinateData.objects.all()
    
    def find_by_lon_and_lat(lon: str, lat: str):
        return CoordinateData.objects.filter(lon=lon, lat=lat)


class OrganizationDataWrapper:
    def save(data):
        for organization in data['result']:
            od = OrganizationData(
                name = organization['name'].lower(),
                address = organization['address'].lower(),
                type = Activity.objects.filter(name=organization['type'].lower()),
                lon = organization['points']['lon'],
                lat = organization['points'['lat']]
            )

            od.save()


class RentalPriceDataWrapper:
    def save(data):
        pass


class HousePopulationDataWrapper:
    def save(data):
        pass
