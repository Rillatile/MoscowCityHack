from os import access, name
import numpy as np
import redis

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
    Subway, BarLayers, CafeLayers, BakeryLayers, SupermarketLayers, DentistryLayers, BeautySaloonLayers,
    BarbershopLayers
)


class CoordinateDataWrapper:
    def save(data):
        cd = CoordinateData(
            lat=data['lat'].replace(',', '.'),
            lon=data['lon'].replace(',', '.'),
            processed_value=data['value'],
            metric=data['metric']
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

    def some(number=30):
        start_point = settings.EDGE_LEFT_UP
        end_point = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        all_offices = list(OfficesData.objects.filter(lat__lte=start_point[0], lat__gte=end_point[0]+lat_step,
                                                      lon__gte=start_point[1], lon__lte=end_point[1]-lon_step).values())
        return all_offices[:number]


class ConnectionsLogWrapper:
    def parse_connections(path):
        st = datetime.now()
        with open(path, 'r') as f:
            connections_db = []
            lines = f.readlines()
            devices = Device.objects.all()
            users = User.objects.all()
            waps = WAP.objects.all()

            for i, line in enumerate(lines):
                if i % 100 == 0:
                    print(i)
                if i != 0:
                    raw_data = line.split(',')
                    c = Connection(
                        datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
                        user=None if raw_data[3] == 'null' else list(filter(lambda u: u.user_hash == raw_data[3]), users)[0],
                        device=list(filter(lambda d: d.device_hash == raw_data[2], devices))[0],
                        access_point=list(filter(lambda ap: ap.mac == raw_data[1]), waps)[0]
                    )
                    c.save()
                    # c = Connection(
                    #     datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
                    #     access_point=WAP.objects.get(mac=raw_data[1]),
                    #     device=Device.objects.get(device_hash=raw_data[2]),
                    #     user=None if raw_data[3] == 'null' else User.objects.get(user_hash=raw_data[3])
                    # )
                    # c.save()
                    # connections_db.append(
                    #     Connection(
                    #         datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
                    #         access_point=WAP.objects.get(mac=raw_data[1]),
                    #         device=Device.objects.get(device_hash=raw_data[2]),
                    #         user=None if raw_data[3] == 'null' else User.objects.get(user_hash=raw_data[3])
                    #         access_point=list(filter(lambda ap: ap.mac == raw_data[1]), waps_db)[0],
                    #         device=list(filter(lambda d: d.device_hash == raw_data[2], devices_db))[0],
                    #         user=None if raw_data[3] == 'null' else list(filter(lambda u: u.user_hash == raw_data[3]), users_db)[0]
                    #     )
                    # )

                    # if len(connections_db) == 5000:
                    #     Connection.objects.bulk_create(connections_db)
                    #     connections_db.clear()
            
            # # Connection.objects.bulk_create(connections_db)

            # if len(connections_db) > 0:
            #     Connection.objects.bulk_create(connections_db)

            print(datetime.now() - st)

    def parse_connections_log_file(path):
        st = datetime.now()
        with open(path, 'r') as f:
            devices = set()
            users = set()
            lines = f.readlines()
            waps = {}
            for i, line in enumerate(lines):
                if i != 0:
                    raw_data = line.split(',')

                    devices.add(raw_data[2])

                    if raw_data[3] != 'null':
                        users.add(raw_data[3])

                    if raw_data[1] not in waps.keys():
                        waps[raw_data[1]] = {}
                        waps[raw_data[1]]['lat'] = raw_data[4].replace('(', '').replace('"', '').strip()
                        waps[raw_data[1]]['lon'] = raw_data[5].replace(')', '').replace('"', '').strip()

            devices_db = []
            users_db = []
            waps_db = []

            for device in list(devices):
                devices_db.append(Device(device_hash=device))

            for user in list(users):
                users_db.append(User(user_hash=user))

            for key in waps.keys():
                waps_db.append(WAP(mac=key, lat=waps[key]['lat'], lon=waps[key]['lon']))

            Device.objects.bulk_create(devices_db)
            User.objects.bulk_create(users_db)
            WAP.objects.bulk_create(waps_db)

            # connections_db = []

            # for i, line in enumerate(lines):
            #     if i != 0:
            #         raw_data = line.split(',')
            #         connections_db.append(
            #             Connection(
            #                 datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
            #                 access_point=WAP.objects.get(mac=raw_data[1]),
            #                 device=Device.objects.get(device_hash=raw_data[2]),
            #                 user=None if raw_data[3] == 'null' else User.objects.get(user_hash=raw_data[3])
            #                 access_point=list(filter(lambda ap: ap.mac == raw_data[1]), waps_db)[0],
            #                 device=list(filter(lambda d: d.device_hash == raw_data[2], devices_db))[0],
            #                 user=None if raw_data[3] == 'null' else list(filter(lambda u: u.user_hash == raw_data[3]), users_db)[0]
            #             )
            #         )
            
            # Connection.objects.bulk_create(connections_db)

            # print(datetime.now() - st)
            # device = Device.objects.get_or_create(
            #     device_hash=raw_data[2]
            # )[0]
            # user = None
            # if raw_data[3] != 'null':
            #     user = User.objects.get_or_create(
            #         user_hash=raw_data[3]
            #     )[0]
            # wap = WAP.objects.get_or_create(
            #     mac=raw_data[1],
            #     lat=raw_data[4].replace(
            #         '(', '').replace('"', '').strip(),
            #     lon=raw_data[5].replace(')', '').replace(
            #         '"', '').strip(),
            # )[0]
            # connection = Connection(
            #     datetime=datetime.strptime(raw_data[0], '%Y-%m-%d %H:%M:%S%z'),
            #     access_point=wap,
            #     device=device,
            #     user=user
            # )

            # connection.save()
    
    

dts = [BarLayers, CafeLayers, DentistryLayers, BarbershopLayers, BeautySaloonLayers, SupermarketLayers, BakeryLayers]
table_names = ['BarLayers', 'CafeLayers', 'DentistryLayers', 'BarbershopLayers', 'BeautySaloonLayers', 'SupermarketLayers', 'BakeryLayers']


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
                round(start_point[0] - lat_step * ((start_point[0] - float(point.lat)) // lat_step), 6),
                round(start_point[1] + lon_step * ((float(point.lon) - start_point[1]) // lon_step), 6)
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
            min_value = layers_by_metric.first().value
            max_value = layers_by_metric.last().value
            for i, layer in enumerate(layers_by_metric):
                # (value - min) / (max - min)
                try:
                    layers_by_metric[i].value = (layers_by_metric[i].value - min_value) / (max_value - min_value)
                except ZeroDivisionError:
                    layers_by_metric[i].value = 0
            # Update scaled values data
            Layer.objects.bulk_update(layers_by_metric, ['value'])

    @staticmethod
    def get_general_layers(layers=None):
        for dt in dts:
            dt.objects.all().delete()

        start_point = settings.EDGE_LEFT_UP
        end_point = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        if not layers:
            layers = Layer.objects.select_related('metric').all()
        metrics = Metric.objects.all()
        activities = list(Activity.objects.all().values('id', 'config', 'name'))
        lats = np.arange(start_point[0], end_point[0], -lat_step)
        lons = np.arange(start_point[1], end_point[1], lon_step)

        for i, activity in enumerate(activities):
            act_layers = []

            for k in lats:
                for j in lons:
                    act_layers.append(
                        dts[i].objects.create(lat=round(k, 6), lon=round(j, 6), metric=metrics[0], value=0)
                    )
            for metric in metrics:
                for j, act_layer in enumerate(act_layers):
                    # находим слой с такой же метрикой и такой же стартовой точкой в общей таблице по слоям
                    layer = layers.filter(metric=metric, lat=act_layer.lat, lon=act_layer.lon).first()
                    # суммируем исходное значение со значением в секторе по метрике с учетом коэффициента конкретного
                    # вида деятельности
                    act_layers[j].value = act_layers[j].value + activity['config'][metric.id - 1] * layer.value
                # найдем среднее арифметическое для каждого сектора общей карты
                for j, _ in enumerate(act_layers):
                    act_layers[j].value = act_layers[j].value / metrics.count()
            dts[i].objects.bulk_update(act_layers, ['value'])


class ActivitiesWrapper:

    def all():
        activities = Activity.objects.select_related('scope')
        data = list(activities.values('id', 'name', 'scope_id', 'config', scope_name=F('scope__name')))
        return data


class HeatMapWrapper:
    def generate_map(is_zero=True):
        layers = LayerBuilder.generate_layers(is_zero=is_zero)
        return layers

    def get_rand_heatmap(act_id):  # генерация случайной карты
        LayerBuilder.generate_layers(is_zero=False, on_delete=True)
        return list(Layer.objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))

    def get_from_db(act_id):  # достать карту для выбранной активности
        j = next(i for i, x in enumerate(table_names) if x == (Activity.objects.get(id=act_id)).table_name)
        return list(dts[j].objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))

    def get_sector_data(sector_id, act_id):
        data = {'metrics': [], 'general_value': 0}
        activity = Activity.objects.get(id=act_id)
        j = next(i for i, x in enumerate(table_names) if x == activity.table_name)

        data = dts[j].objects.get(id=sector_id)
        datas = Layer.objects.all()
        for i, d in enumerate(datas):
            if (d.lat == data.lat) and (d.lon == data.lon):
                break

        data['general'] = (dts[j].objects.get(id=sector_id)).value
        config = activity.config
        metrics = Metric.objects.all()
        layers = Layer.objects.all()
        for k, _ in enumerate(metrics):
            value_from_layers_table = layers[i].value
            value = value_from_layers_table*config[k]
            data['metrics'].append({'metric_id': _.id, 'value': value})
        return data


class SubwayWrapper:
    def save(data):
        for subway in data['result']:
            s = Subway(
                lon=str(subway['lon']).replace(',', '.'),
                lat=str(subway['lat']).replace(',', '.')
            )

            s.save()
