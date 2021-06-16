import numpy as np

from datetime import datetime

from django.conf import settings

from django.db.models import F

from .models import (
    Activity,
    Connection,
    CoordinateData,
    Device,
    FlatsData,
    OfficesData,
    OrganizationData,
    User,
    RentalData,
    WAP,
    Layer,
    Metric,
    Subway,
    BarLayers, CafeLayers, BakeryLayers, SupermarketLayers, DentistryLayers, BeautySaloonLayers,
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
                                                      lon__gte=start_point[1], lon__lte=end_point[1]-lon_step).order_by('?').values())
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
    @staticmethod
    def generate_borders():
        start = settings.EDGE_LEFT_UP
        end = settings.EDGE_RIGHT_DOWN
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        is_correct = True
        start_point = start
        end_point = end
        steps = [lat_step, lon_step]

        # Check if the step more than area width or height
        if lat_step > start_point[0] - end_point[0]:
            return (not is_correct), start_point, end_point, steps
        if lon_step > end_point[1] - start_point[1]:
            return (not is_correct), start_point, end_point, steps

        # Check if an area cannot be separated into whole number of sectors - then expand the area
        if lat_step * ((start_point[0] - end_point[0]) // lat_step) != start_point[0] - end_point[0]:
            end_point[0] = start_point[0] - lat_step * ((start_point[0] - end_point[0]) // lat_step + 1)
        if lon_step * ((end_point[1] - start_point[1]) // lon_step) != end_point[1] - start_point[1]:
            end_point[1] = start_point[1] + lon_step * ((end_point[1] - start_point[1]) // lon_step + 1)
        return is_correct, start_point, end_point, steps

    @staticmethod
    def process_coordinates():
        # Generate empty layers with deleting old layers in db
        LayerBuilder.generate_layers(on_delete=True, is_zero=True)
        # Fill that layers with coordinates data
        LayerBuilder.group_coord_by_sectors()
        return Layer.objects.select_related('metric').all()

    @staticmethod
    def generate_layers(metrics=None, on_delete=False, is_zero=False):
        if on_delete:
            Layer.objects.all().delete()

        if not metrics:
            metrics = Metric.objects.all()
        activities = Activity.objects.all()

        is_correct, start_point, end_point, steps = LayerBuilder.generate_borders()
        if not is_correct:
            return -1
        lats = np.arange(start_point[0], end_point[0], -steps[0])
        lons = np.arange(start_point[1], end_point[1], steps[1])
        # Create layers ith all metrics
        layers = []
        for i in lats:
            for j in lons:
                for m in metrics:
                    points = CoordinateData.objects.select_related('activity').filter(metric=m).first()
                    if not is_zero:
                        value = np.random.random()
                    else:
                        value = 0
                    if points.activity is not None:
                        for a in activities:
                            layers.append(Layer.objects.create(lat=round(i, 6), lon=round(j, 6), metric=m, value=value, activity=a))
                    else:
                        layers.append(Layer.objects.create(lat=round(i, 6), lon=round(j, 6), metric=m, value=value))
        return layers

    @staticmethod
    def group_coord_by_sectors(coordinate_data=None, layers=None):
        start_point = settings.EDGE_LEFT_UP
        lat_step = settings.LAT_DISTANCE
        lon_step = settings.LON_DISTANCE

        if not layers:
            layers = list(Layer.objects.select_related('activity', 'metric').all())
        if not coordinate_data:
            coordinate_data = CoordinateData.objects.select_related('activity', 'metric').all()

        layer_counter = [0 for _ in range(len(layers))]
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
            for l_i, layer in enumerate(layers):
                if (layer.lat == left_up_point[0]) and (layer.lon == left_up_point[1]) and (layer.metric == point.metric):
                    if (point.activity is not None) and (layer.activity is not None):
                        if point.activity.id == layer.activity.id:
                            break
                    else:
                        break
            # Increment layers[i].value and layer_counter value
            layers[l_i].value = layers[l_i].value + point.processed_value
            layer_counter[l_i] = layer_counter[l_i] + 1
        # Count average Layer value
        # There is chance to "play" with data - you can use median, min, max etc values instead of average
        for i, layer in enumerate(layers):
            if layer.metric.generalizing_oper == 'ave':
                try:
                    layers[i].value = layers[i].value / layer_counter[i]
                except ZeroDivisionError:
                    layers[i].value = 0
        Layer.objects.bulk_update(layers, ['value'])

    @staticmethod
    def scale_layers(layers_by_metric):
        min_value = layers_by_metric.first().value
        max_value = layers_by_metric.last().value
        for i, layer in enumerate(layers_by_metric):
            # (value - min) / (max - min)
            try:
                layers_by_metric[i].value = (layers_by_metric[i].value - min_value) / (
                        max_value - min_value)
            except ZeroDivisionError:
                layers_by_metric[i].value = 0
        # Update scaled values data
        Layer.objects.bulk_update(layers_by_metric, ['value'])

    @staticmethod
    def scale_values():
        """Scale data with value [0, 1]"""
        layers = Layer.objects.select_related('metric').all()
        metrics = Metric.objects.all()
        activities = Activity.objects.all()
        # For each metric find min and max values
        for metric in metrics:
            points = CoordinateData.objects.select_related('activity').filter(metric=metric).first()
            if points.activity is not None:
                for a in activities:
                    layers_by_metric = layers.filter(metric=metric, activity=a).exclude(value=0).order_by('value')
                    LayerBuilder.scale_layers(layers_by_metric)
            else:
                layers_by_metric = layers.filter(metric=metric).exclude(value=0).order_by('value')
                LayerBuilder.scale_layers(layers_by_metric)

    @staticmethod
    def get_general_layers(layers=None):
        for dt in dts:
            dt.objects.all().delete()
        is_correct, start_point, end_point, steps = LayerBuilder.generate_borders()
        if not is_correct:
            return -1
        lats = np.arange(start_point[0], end_point[0], -steps[0])
        lons = np.arange(start_point[1], end_point[1], steps[1])
        if not layers:
            layers = Layer.objects.select_related('metric', 'activity').all()
        metrics = Metric.objects.all()
        activities = list(Activity.objects.all().values())
        for i, activity in enumerate(activities):
            act_layers = []
            for t_i, table_name in enumerate(table_names):
                if activity['table_name'] == table_name:
                    break
            for lat in lats:
                for lon in lons:
                    act_layers.append(dts[t_i].objects.create(lat=round(lat, 6), lon=round(lon, 6), metric=metrics[0], value=0))
            counter = [0 for _ in range(len(act_layers))]

            # Теперь расчитываем значения value ля каждого вида деятельности
            for m_i, metric in enumerate(metrics):
                for al_i, activity_layer in enumerate(act_layers):
                    # находим слой с такой же метрикой и такой же стартовой точкой в общей таблице по слоям
                    points = CoordinateData.objects.select_related('activity').filter(metric=metric).first()
                    if points.activity is not None:
                        layer = layers.filter(metric=metric, lat=act_layers[al_i].lat, lon=act_layers[al_i].lon, activity__id=activity['id']).first()
                    else:
                        layer = layers.filter(metric=metric, lat=act_layers[al_i].lat, lon=act_layers[al_i].lon).first()
                    # суммируем исходное значение со значением в секторе по метрике с учетом коэффициента конкретного
                    # вида деятельности
                    if activity['config'][m_i] * layer.value > 0:
                        act_layers[al_i].value = act_layers[al_i].value + (activity['config'][m_i]/4.0) * layer.value
                        counter[al_i] = counter[al_i] + 1
            # найдем среднее арифметическое для каждого сектора общей карты
            for j, _ in enumerate(act_layers):
                try:
                    act_layers[j].value = act_layers[j].value / (counter[j])
                except ZeroDivisionError:
                    act_layers[j].value = 0
            dts[t_i].objects.bulk_update(act_layers, ['value'])


class ActivitiesWrapper:
    @staticmethod
    def all():
        activities = Activity.objects.select_related('scope')
        data = list(activities.values('id', 'name', 'scope_id', 'config', scope_name=F('scope__name')))
        return data


class HeatMapWrapper:
    @staticmethod
    def generate_map(is_zero=True):
        layers = LayerBuilder.generate_layers(is_zero=is_zero)
        return layers

    @staticmethod
    def get_rand_heatmap(act_id=None):  # генерация случайной карты
        LayerBuilder.generate_layers(is_zero=False, on_delete=True)
        return list(Layer.objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))

    @staticmethod
    def get_from_db(act_id):  # достать карту для выбранной активности
        activity = Activity.objects.get(id=act_id)
        for j, name in enumerate(table_names):
            if activity.table_name == name:
                return list(dts[j].objects.all().values('id', 'lon', 'lat', 'lon_distance', 'lat_distance', 'value'))
        return []

    @staticmethod
    def get_sector_data(sector_id, act_id):
        out_data = {'metrics': [], 'general_value': 0}
        activity = Activity.objects.get(id=act_id)
        for j, name in enumerate(table_names):
            if activity.table_name == name:
                break

        data = dts[j].objects.get(id=sector_id)
        layers = Layer.objects.all().filter(lat=data.lat, lon=data.lon)

        config = activity.config
        layers_without_metric = []
        metrics = Metric.objects.all()
        for k, _ in enumerate(metrics):
            point = CoordinateData.objects.select_related('activity', 'metric').filter(metric=_).first()
            if point.activity is not None:
                layer = layers.filter(metric=_, activity=point.activity).first()
            else:
                layer = layers.filter(metric=_).first()
            layers_without_metric.append(layer.value)
        counter = 0
        for l in layers_without_metric:
            if l>0:
                counter = counter + 1
        general = 0
        for k, _ in enumerate(metrics):
            counted_layer = layers_without_metric[k]*config[k] / 4.0
            out_data['metrics'].append({'metric': _.id, 'value': counted_layer})
            general = general + counted_layer
        out_data['general_value'] = general / counter
        return out_data


    # @staticmethod
    # def get_sector_data(sector_id, act_id):
    #     out_data = {'metrics': [], 'general_value': 0}
    #     activity = Activity.objects.get(id=act_id)
    #     for j, name in enumerate(table_names):
    #         if activity.table_name == name:
    #             break
    #     # j = next(i for i, x in enumerate(table_names) if x == activity.table_name)
    #
    #     data = dts[j].objects.get(id=sector_id)
    #     out_data['general_value'] = data.value
    #     layers = Layer.objects.all().filter(lat=data.lat, lon=data.lon)
    #
    #     config = activity.config
    #     metrics = Metric.objects.all()
    #     # layers = Layer.objects.all()
    #     for k, _ in enumerate(metrics):
    #         layer = layers.filter(metric_id=_.id).first()
    #         # value_from_layers_table = layers[i].value
    #         value_from_layers_table = layer.value
    #         value = value_from_layers_table*config[k]
    #         out_data['metrics'].append({'metric_id': _.id, 'value': value/5})
    #     return out_data


class SubwayWrapper:
    def save(data):
        for subway in data['result']:
            s = Subway(
                lon=str(subway['lon']).replace(',', '.'),
                lat=str(subway['lat']).replace(',', '.')
            )

            s.save()
