from dateutil.parser import parse
from datetime import datetime
from os import access

from django.conf import settings
from django.db import connection
from .models import (
    Activity,
    Connection,
    CoordinateData,
    Device,
    OrganizationData,
    User,
    WAP,
    Layer,
    Metric
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
                        lat=raw_data[4].replace(
                            '(', '').replace('"', '').strip(),
                        lon=raw_data[5].replace(')', '').replace(
                            '"', '').strip(),
                    )
                    connection = Connection(
                        datetime=parse(raw_data[0]),
                        access_point=wap,
                        device=device,
                        user=user
                    )

                    connection.save()


class LayerBuilder:
    @staticmethod
    def group_coord_by_sectors(coordinate_data=None):
        start_point = settings.EDGE_LEFT_UP
        end_point = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        if not coordinate_data:
            coordinate_data = CoordinateData.objects.select_related('metric').all()
        # Create layer sectors
        metrics = Metric.objects.all()
        # Check if the step more than area width or height
        if lat_step > start_point[0]-end_point[0]:
            return -1
        if lon_step > end_point[1]-start_point[1]:
            return -1
        # Check if an area cannot be separated into whole number of sectors - then expand the area
        if lat_step * ((start_point[0]-end_point[0])//lat_step) != start_point[0]-end_point[0]:
            end_point[0] = start_point[0] - lat_step*((start_point[0] - end_point[0])//lat_step + 1)
        if lon_step * ((end_point[1]-start_point[1])//lon_step) != end_point[1]-start_point[1]:
            end_point[1] = start_point[0] + lon_step*((end_point[1] - start_point[1])//lon_step + 1)

        layers = [
            Layer.objects.create(lat=i, lon=j, metric=m, value=0)
            for i in range(start_point[0], end_point[0], -lat_step)
            for j in range(start_point[1], end_point[1], lon_step)
            for m in metrics
        ]
        layer_counter = [0 for _ in range(len(layers))]
        # Count layers[i].value
        for point in coordinate_data:
            # Count where the point is placed (section start coordinates)
            # start + ((point - start)//step)*step for lon coord
            # start - ((start - point)//step)*step for lat coord
            left_up_point = [
                start_point[0] - lat_step*((start_point[0] - point.lat)//lat_step),
                start_point[1] + lon_step*((point.lon - start_point[1])//lon_step)
            ]
            # Search a layer with such coordinates
            # todo: округление!!!!
            for k, layer in enumerate(layers):
                if (layer.lat == left_up_point[0]) and (layer.lon == left_up_point[1]) and (layer.metric == point.metric):
                    break
            # Increment layers[i].value
            layers[k].value = layers[k].value + point.processed_value
            layer_counter[k] = layer_counter[k] + 1
        # Count average Layer value
        # There is chance to "play" with data - you can use median, min, max etc values instead of average
        for i, _ in enumerate(layers):
            layers[i] = layers[i].value / layer_counter[i]
        # Update it
        Layer.objects.bulk_update(layers, ['value'])

    @staticmethod
    def scale_values(layers=None):
        """Scale data with value [0, 1]"""
        if not layers:
            layers = Layer.objects.select_related('metric').all()
        metrics = Metric.objects.all()
        # For each metric find min and max values
        for metric in metrics:
            layers_by_metric = layers.filter(metric=metric).order_by('value')
            min_value = layers_by_metric.first()
            max_value = layers_by_metric.last()
            for i, layer in enumerate(layers_by_metric):
                # (value - min) / (max - min)
                layers_by_metric[i].value = (layers_by_metric[i].value-min_value) / (max_value-min_value)
            # Update scaled values data
            Layer.objects.bulk_update(layers_by_metric, ['value'])

    @staticmethod
    def get_general_layers():
        ...
