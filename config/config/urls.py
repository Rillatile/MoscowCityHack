from django.contrib import admin
from django.urls import path, include

from api.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('', index)
]
