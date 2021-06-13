from os import name
import numpy as np

from datetime import datetime

from django.conf import settings

from django.db import connection
from django.db.models import F

from .models import (
    Activity,
    Connection,
    CoordinateData,
    Device,
    FlatsData,
    OfficesData,
    OrganizationData,
    Subway,
    User,
    RentalData,
    WAP,
    Layer,
    Metric,
    Scope,
    Subway, BarLayers, CafeLayers, BakeryLayers, SupermarketLayers, DentistryLayers, BeautySaloonLayers
)


class CoordinateDataWrapper:
    def save(data):
        cd = CoordinateData(
            lat=data['lat'].replace(',', '.'),
            lon=data['lon'].replace(',', '.'),
            processed_value=data['value'],
            metric = data['metric']
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
                name=organization['name'].lower(),
                address=organization['address'].lower(),
                type=Activity.objects.get(name=organization['type'].lower()),
                lon=str(organization['point']['lon']).replace(',', '.'),
                lat=str(organization['point']['lat']).replace(',', '.')
            )

            od.save()


class RentalPriceDataWrapper:
    def save(data):
        for rent in data['result']:
            rpd = RentalData(
                price=rent['price'],
                address=rent['address'].lower(),
                lon=str(rent['point']['lng']).replace(',', '.'),
                lat=str(rent['point']['lat']).replace(',', '.')
            )

            rpd.save()

            CoordinateDataWrapper.save({
                'lat': str(rent['point']['lat']).replace(',', '.'),
                'lon': str(rent['point']['lng']).replace(',', '.'),
                'value': rent['price'],
                'metric': Metric.objects.get(name='платежеспособность')
            })


class HousePopulationDataWrapper:
    def save(data):
        for house in data['result']:
            hpd = FlatsData(
                flats=house['flats'],
                address=house['address'].lower(),
                lon=str(house['point']['lon']).replace(',', '.'),
                lat=str(house['point']['lat']).replace(',', '.')
            )

            hpd.save()

            CoordinateDataWrapper.save({
                'lat': str(house['point']['lat']).replace(',', '.'),
                'lon': str(house['point']['lon']).replace(',', '.'),
                'value': house['flats'],
                'metric': Metric.objects.get(name='население')
            })
            
class OfficesDataWrapper:
    def save(data):
        for office in data['result']:
            od = OfficesData(
                price=office['price'],
                area=office['area'],
                link=office['url'],
                address=office['address'].lower(),
                lon=str(office['point']['lng']).replace(',', '.'),
                lat=str(office['point']['lat']).replace(',', '.')
            )

            od.save()


class ConnectionsLogWrapper:
    def parse_connections_log_file(path):
        with open(path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if i != 0:
                    raw_data = line.split(',')
                    device = Device.objects.get_or_create(
                        device_hash=raw_data[2]
                    )[0]
                    user = None
                    if raw_data[3] != 'null':
                        user = User.objects.get_or_create(
                            user_hash=raw_data[3]
                        )[0]
                    wap = WAP.objects.get_or_create(
                        mac=raw_data[1],
                        lat=raw_data[4].replace(
                            '(', '').replace('"', '').strip(),
                        lon=raw_data[5].replace(')', '').replace(
                            '"', '').strip(),
                    )[0]
                    connection = Connection(
                        datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
                        access_point=wap,
                        device=device,
                        user=user
                    )

                    connection.save()

dts = [BakeryLayers, SupermarketLayers, DentistryLayers, BeautySaloonLayers, CafeLayers, BarLayers]

class LayerBuilder:
    def process_coordinates():
        # Generate empty layers with deleting old layers in db
        LayerBuilder.generate_layers(on_delete=True, is_zero=True)
        # Fill that layers with coordinates data
        LayerBuilder.group_coord_by_sectors()
        return Layer.objects.select_related('metric').all()

    def generate_layers(metrics=None, on_delete=False, is_zero=False):
        if on_delete:
            Layer.objects.all().delete()
        start_point = settings.EDGE_LEFT_UP
        end_point = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        if not metrics:
            metrics = Metric.objects.all()

        # Check if the step more than area width or height
        if lat_step > start_point[0] - end_point[0]:
            return -1
        if lon_step > end_point[1] - start_point[1]:
            return -1
        # Check if an area cannot be separated into whole number of sectors - then expand the area
        if lat_step * ((start_point[0] - end_point[0]) // lat_step) != start_point[0] - end_point[0]:
            end_point[0] = start_point[0] - lat_step * ((start_point[0] - end_point[0]) // lat_step + 1)
        if lon_step * ((end_point[1] - start_point[1]) // lon_step) != end_point[1] - start_point[1]:
            end_point[1] = start_point[1] + lon_step * ((end_point[1] - start_point[1]) // lon_step + 1)

        lats = np.arange(start_point[0], end_point[0], -lat_step)
        lons = np.arange(start_point[1], end_point[1], lon_step)
        layers = []
        for i in lats:
            for j in lons:
                for m in metrics:
                    if not is_zero:
                        value = np.random.random()
                    else:
                        value = 0
                    layers.append(Layer.objects.create(lat=round(i, 6), lon=round(j, 6), metric=m, value=value))

    def group_coord_by_sectors(coordinate_data=None, layers=None):
        start_point = settings.EDGE_LEFT_UP
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE
        if not layers:
            layers = Layer.objects.all()
        layer_counter = [0 for _ in range(len(layers))]
        if not coordinate_data:
            coordinate_data = CoordinateData.objects.all()
        # Count layers[i].value
        for point in coordinate_data:
            # Count where the point is placed (section start coordinates)
            # start + ((point - start)//step)*step for lon coord
            # start - ((start - point)//step)*step for lat coord
            left_up_point = [
                round(start_point[0] - lat_step*((start_point[0] - float(point.lat))//lat_step), 6),
                round(start_point[1] + lon_step*((float(point.lon) - start_point[1])//lon_step), 6)
            ]
            # Search a layer with such coordinates
            for k, layer in enumerate(layers):
                if (round(layer.lat, 6) == left_up_point[0]) and (round(layer.lon, 6) == left_up_point[1]) and \
                        (layer.metric == point.metric):
                    break
            # Increment layers[i].value and layer_counter value
            layers[k].value = layers[k].value + point.processed_value
            layer_counter[k] = layer_counter[k] + 1
        # Count average Layer value
        # There is chance to "play" with data - you can use median, min, max etc values instead of average
        for i, layer in enumerate(layers):
            if point.metric.generalizing_oper == 'ave':
                old_value = layer.value
                try:
                    layers[i].value = layers[i].value / layer_counter[i]
                except ZeroDivisionError:
                    layers[i].value = 0
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
    def get_general_layers(layers=None):
        start_point = settings.EDGE_LEFT_UP
        end_point = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        if not layers:
            layers = Layer.objects.select_related('metric').all()
        metrics = Metric.objetcs.all()
        activities = Activity.objects.all()
        lats = np.arange(start_point[0], end_point[0], -lat_step)
        lons = np.arange(start_point[1], end_point[1], lon_step)

        for a_i, activity in enumerate(activities):
            zero_act_layer = []
            for i in lats:
                for j in lons:
                    for m in metrics:
                        zero_act_layer.append(
                            dts[j].objects.create(lat=round(i, 6), lon=round(j, 6), metric=m, value=0,
                                                   activity_id=1))

        for i, activity in enumerate(activities):
            act_layers = zero_act_layer
            for metric in metrics:
                for j, act_layer in enumerate(act_layers):
                    # находим слой с такой же метрикой и такой же стартовой точкой в общей таблице по слоям
                    layer = layers.filter(metric=metric, lat=act_layer.lat , lon=act_layer)
                    # суммируем исходное значение со значением в секторе по метрике с учетом коэффициента конкретного
                    # вида деятельности
                    act_layers[j].value = act_layers[j].value + activity.config[metric.id] * layer.value
                # найдем среднее арифметическое для каждого сектора общей карты
                for j, _ in enumerate(act_layers):
                    act_layers[j].value = act_layers[j].value / metrics.count()
                    act_layers[j].activity = activity
            dts[i].objects.bulk_update(layers, ['value', 'activity'])


class ActivitiesWrapper:

    def all():
        activities = Activity.objects.select_related('scope')
        data = list(activities.values('id', 'name', 'scope_id', 'config', scope_name=F('scope__name')))
        return data


class HeatMapWrapper:
    def generate_map(is_zero=True):
        layers = LayerBuilder.generate_layers(is_zero=is_zero)
        return layers

    def get_rand_heatmap(act_id):    # генерация случайной карты
        LayerBuilder.generate_layers(is_zero=False, on_delete=True)
        return list(Layer.objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))

    def get_from_db(act_id):        # достать карту для выбранной активности
        return list(dts[act_id].objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))


class SubwayWrapper:
    def save(data):
        for subway in data['result']:
            s = Subway(
                lon=str(subway['lon']).replace(',', '.'),
                lat=str(subway['lat']).replace(',', '.')
            )

            s.save()
