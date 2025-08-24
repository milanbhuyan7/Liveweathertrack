from rest_framework import serializers
from .models import City, WeatherData, ForecastData, UserPreference

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'country_code', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'created_at']

class WeatherDataSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    
    class Meta:
        model = WeatherData
        fields = [
            'id', 'city', 'temperature', 'feels_like', 'humidity', 'pressure',
            'weather_main', 'weather_description', 'weather_icon', 'wind_speed',
            'wind_direction', 'visibility', 'uv_index', 'cached_at'
        ]

class ForecastDataSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    
    class Meta:
        model = ForecastData
        fields = [
            'id', 'city', 'forecast_date', 'temperature_min', 'temperature_max',
            'temperature_day', 'temperature_night', 'humidity', 'pressure',
            'weather_main', 'weather_description', 'weather_icon', 'wind_speed',
            'wind_direction', 'cached_at'
        ]

class UserPreferenceSerializer(serializers.ModelSerializer):
    favorite_cities = CitySerializer(many=True, read_only=True)
    
    class Meta:
        model = UserPreference
        fields = ['id', 'session_key', 'favorite_cities', 'temperature_unit', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class AddCitySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    country_code = serializers.CharField(max_length=2)
    
    def validate_country_code(self, value):
        return value.upper()
