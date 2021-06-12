from django.conf import settings

from .models import CoordinateData, Layer, Metric


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
        pass


class RentalPriceDataWrapper:
    def save(data):
        pass


class HousePopulationDataWrapper:
    def save(data):
        pass


class LayerBuilder:
    @staticmethod
    def group_coord_by_sectors(coordinate_data=None):
        if not coordinate_data:
            coordinate_data = CoordinateData.objects.select_related('metric').all()
        # Create layer sectors
        metrics = Metric.objects.all()
        # todo: round the last border to up
        layers = [Layer.objects.create(lat=i, lon=j, metric=m, value=0)
                  for i in range(settings.EDGE_RIGHT_DOWN[0],
                                 settings.EDGE_LEFT_UP[0],
                                 settings.LAT_DISTANCE)
                  for j in range(settings.EDGE_RIGHT_DOWN[1],
                                 settings.EDGE_LEFT_UP[1],
                                 settings.LON_DISTANCE)
                  for m in metrics]
        layer_counter = [0 for _ in range(len(layers))]
        # Count layers[i].value
        for point in coordinate_data:
            # Count where the point is placed (section start coordinates)
            # ((point - start)/step -1)*step + start
            left_up_point = [settings.EDGE_RIGHT_DOWN +
                             settings.LAT_DISTANCE * (
                                         (point.lat - settings.EDGE_RIGHT_DOWN[0]) / settings.LAT_DISTANCE - 1),
                             settings.EDGE_RIGHT_DOWN +
                             settings.LON_DISTANCE * (
                                         (point.lat - settings.EDGE_RIGHT_DOWN[1]) / settings.LON_DISTANCE - 1),
                             ]
            # Search a layer with such coordinates
            for k, layer in enumerate(layers):
                if (layer.lat == left_up_point[0]) and (layer.lon == left_up_point[1]) and (
                        layer.metric == point.metric):
                    break
            # layers[i].value++
            layers[k].value = layers[k].value + point.processed_value
            layer_counter[k] = layer_counter[k] + 1
        # Count average Layer value
        # There is chance to "play" with data - you can use median, min, max etc values instead of average
        for i, layer in enumerate(layers):
            layer = layer / layer_counter[i]
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
            for layer in layers_by_metric:
                layer.value = (layer.value - min_value)/max_value
        # Update scaled values data
        Layer.objects.bulk_update(layers, ['value'])

    @staticmethod
    def get_quartiles():
        """Find and return all layer objects in the first or in the third quartile (1th - when metric optmin_config =
        False, and 3th - when metric optim_config - True) """
        ...
