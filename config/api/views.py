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
            ConnectionsLogWrapper.parse_connections_log_file(
                request.data['path'])
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
        act_id = kwargs['act_id']
        data = HeatMapWrapper.get_heatmap(act_id)
        return JsonResponse({'data': data}, safe=False)


def generate_zero_layers(request, on_delete):
    LayerBuilder.generate_zero_layers(None, on_delete)
    return HttpResponse('done', status=status.HTTP_200_OK)


class SubwayView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        try:
            SubwayWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
