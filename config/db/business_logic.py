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
            for k, layer in enumerate(layers):
                if (layer.lat == left_up_point[0]) and (layer.lon == left_up_point[1]) and (
                        layer.metric == point.metric):
                    break
            # layers[i].value++
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
            for layer in layers_by_metric:
                layer.value = (layer.value - min_value)/max_value
        # Update scaled values data
        Layer.objects.bulk_update(layers, ['value'])

    @staticmethod
    def get_quartiles():
        """Find and return all layer objects in the first or in the third quartile (1th - when metric optmin_config =
        False, and 3th - when metric optim_config - True) """
        ...

