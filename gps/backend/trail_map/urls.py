# urls.py
from django.urls import path

from . import views

app_name = 'trail_map'
urlpatterns = [
    path('save_location/', views.SaveLocationDataView.as_view(), name='save_location_data'),
    path('get_locations/', views.GetLocationDataView.as_view(), name='get_locations_data'),
]
