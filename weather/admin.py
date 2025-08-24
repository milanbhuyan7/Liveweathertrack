from django.contrib import admin
from .models import City, WeatherData, ForecastData, UserPreference

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_code', 'latitude', 'longitude', 'created_at']
    list_filter = ['country_code', 'created_at']
    search_fields = ['name', 'country_code']

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'temperature', 'weather_main', 'cached_at']
    list_filter = ['weather_main', 'cached_at']
    search_fields = ['city__name']

@admin.register(ForecastData)
class ForecastDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'forecast_date', 'temperature_min', 'temperature_max', 'weather_main']
    list_filter = ['weather_main', 'forecast_date']
    search_fields = ['city__name']

@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'temperature_unit', 'created_at']
    list_filter = ['temperature_unit', 'created_at']
