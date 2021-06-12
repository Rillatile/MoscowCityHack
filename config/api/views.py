from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from db.business_logic import CoordinateDataWrapper


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
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class SendRentalPriceDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class SendHousePopulationDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)



