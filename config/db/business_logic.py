from datetime import datetime
from os import access

from django.db import connection
from .models import (
    Activity,
    Connection,
    CoordinateData,
    Device,
    OrganizationData,
    User,
    WAP
)


class CoordinateDataWrapper:
    def save(data):
        cd = CoordinateData(
            lat=data['lat'].replace(',', '.'),
            lon=data['lon'].replace(',', '.'),
            street=data['street'].lower(),
            house=data['house'].lower(),
            raw_values=data['raw_values'],
            processed_value=data['value']
        )

        cd.save()

    def all():
        return CoordinateData.objects.all()

    def find_by_lon_and_lat(lon: str, lat: str):
        return CoordinateData.objects.filter(lon=lon, lat=lat)


class OrganizationDataWrapper:
    def save(data):
        for organization in data['result']:
            print(organization)
            od = OrganizationData(
                name=organization['name'].lower(),
                address=organization['address'].lower(),
                type=Activity.objects.get(name=organization['type'].lower()),
                lon=str(organization['point']['lon']).replace(',', '.'),
                lat=str(organization['point']['lat']).replace(',', '.')
            )

            od.save()


class RentalPriceDataWrapper:
    def save(data):
        pass


class HousePopulationDataWrapper:
    def save(data):
        pass


class ConnectionsLogWrapper:
    def parse_connections_log_file(path):
        with open(path, 'r') as f:
            for i, line in enumerate(f):
                if i != 0:
                    raw_data = line.split(',')
                    device = Device.objects.get_or_create(
                        device_hash=raw_data[2]
                    )
                    user = None
                    if raw_data[3] != 'null':
                        user = User.objects.get_or_create(
                            user_hash=raw_data[3]
                        )
                    wap = WAP.objects.get_or_create(
                        mac=raw_data[1],
                        lat=raw_data[4].replace('(', '').strip(),
                        lon=raw_data[5].replace(')', '').strip(),
                    )
                    connection = Connection(
                        datetime=datetime.strptime(
                            raw_data[0], '%Y-%m-%d %H:%M:%S'),
                        access_point=wap,
                        device=device,
                        user=user
                    )

                    connection.save()
