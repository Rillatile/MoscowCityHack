from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from db.business_logic import (
    ConnectionsLogWrapper,
    CoordinateDataWrapper,
    HousePopulationDataWrapper,
    OfficesDataWrapper,
    OrganizationDataWrapper,
    RentalPriceDataWrapper,
    ActivitiesWrapper,
    HeatMapWrapper,
    LayerBuilder,
    SubwayWrapper
)


class SendCoordinateDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            CoordinateDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendOrganizationDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            OrganizationDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendRentalPriceDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            RentalPriceDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendHousePopulationDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            HousePopulationDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ParseConnectionsLogFileView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            # ConnectionsLogWrapper.parse_connections_log_file(
            #     request.data['path'])
            ConnectionsLogWrapper.parse_connections(request.data['path'])
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendOfficesDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            OfficesDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActivitiesView(APIView):

    def get(self, request):
        data = ActivitiesWrapper.all()
        return JsonResponse({'data': data}, safe=False)


class HeatMapView(APIView):

    def get(self, request, *args, **kwargs):
        act_id = int(request.GET['act_id'])
        data = HeatMapWrapper.get_from_db(act_id)
        return JsonResponse({'data': data}, safe=False)


def generate_zero_layers(request, on_delete):
    LayerBuilder.generate_zero_layers(None, on_delete)
    return HttpResponse('done', status=status.HTTP_200_OK)


# Режим работы 1 - полная генерация данных:
#  - предварительное удаление данных из бд
#  - группировка точечных данных
#  - построение слоев по метрикам и по секциям
#  - построение общих слоев для каждого вида деятельности
def process_data(request):
    data = LayerBuilder.process_coordinates()       # out - сгруппированные точки CoordinateData по секциям и метрикам
    data = LayerBuilder.scale_values(data)          # out - слои с приведенными значениями
    LayerBuilder.get_general_layers(data)           # построить слой с обощенными метриками
    return HttpResponse('done')


class SubwayView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            SubwayWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_sector_data(request):
    sector_id = int(request.GET['sector_id'])
    act_id = int(request.GET['act_id'])
    return JsonResponse({'data': HeatMapWrapper.get_sector_data(sector_id, act_id)}, safe=False)

