from django.urls import path
from .views import (
    SendCoordinateDataView,
    SendHousePopulationDataView,
    SendOrganizationDataView,
    SendRentalPriceDataView
)


urlpatterns = [
    path('send_coordinate_data', SendCoordinateDataView.as_view(), name='send_coordinate_data_view'),
    path('send_house_population_data', SendHousePopulationDataView.as_view(), name='send_house_population_data'),
    path('send_organization_data', SendOrganizationDataView.as_view(), name='send_organization_data'),
    path('send_rental_price_data', SendRentalPriceDataView.as_view(), name='send_rental_price_data')
]
