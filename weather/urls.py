from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, WeatherViewSet, ForecastViewSet, UserPreferenceViewSet

router = DefaultRouter()
router.register(r'cities', CityViewSet)
router.register(r'weather', WeatherViewSet)
router.register(r'forecast', ForecastViewSet)
router.register(r'preferences', UserPreferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
