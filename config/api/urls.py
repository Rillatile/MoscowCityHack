from django.urls import path
from .views import (
    ParseConnectionsLogFileView,
    SendCoordinateDataView,
    SendHousePopulationDataView,
    SendOfficesDataView,
    SendOrganizationDataView,
    SendRentalPriceDataView,
    ActivitiesView,
    HeatMapView,
    generate_zero_layers
)


urlpatterns = [
    path('send_coordinate_data', SendCoordinateDataView.as_view(),
         name='send_coordinate_data_view'),
    path('send_house_population_data', SendHousePopulationDataView.as_view(),
         name='send_house_population_data'),
    path('send_organization_data', SendOrganizationDataView.as_view(),
         name='send_organization_data'),
    path('send_rental_price_data', SendRentalPriceDataView.as_view(),
         name='send_rental_price_data'),
    path('parse_connections_log_file', ParseConnectionsLogFileView.as_view(),
         name='parse_connections_log_file'),
    path('get_activities', ActivitiesView.as_view(), name='get_activities'),
    path('heatmap/<int:act_id>', HeatMapView.as_view(), name='heatmap'),
    path('heatmap/generate/<int:on_delete>', generate_zero_layers, name='generate_heatmap'),
    path('send_offices_data', SendOfficesDataView.as_view(), name='send_offices_data'),
]
