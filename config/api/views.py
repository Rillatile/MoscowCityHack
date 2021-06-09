from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from db.business_logic import CoordinateDataWrapper


class SendCoordinateDataView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, format=None):
        print(CoordinateDataWrapper.find_by_lon_and_lat('37.661104', '55.776088'))
        return Response(status=status.HTTP_201_CREATED)
        try:
            CoordinateDataWrapper.save(request.data)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
