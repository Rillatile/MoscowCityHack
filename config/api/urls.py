from django.urls import path
from .views import SendCoordinateDataView


urlpatterns = [
    path('send_coordinate_data', SendCoordinateDataView.as_view(), name='send_coordinate_data_view'),
]
