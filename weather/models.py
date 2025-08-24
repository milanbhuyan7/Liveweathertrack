from django.db import models
from django.utils import timezone
from datetime import timedelta

class City(models.Model):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'country_code']
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return f"{self.name}, {self.country_code}"

class WeatherData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.FloatField()
    weather_main = models.CharField(max_length=50)  # e.g., "Clear", "Rain"
    weather_description = models.CharField(max_length=100)  # e.g., "clear sky"
    weather_icon = models.CharField(max_length=10)  # e.g., "01d"
    wind_speed = models.FloatField()
    wind_direction = models.IntegerField()
    visibility = models.IntegerField(null=True, blank=True)
    uv_index = models.FloatField(null=True, blank=True)
    cached_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-cached_at']
    
    def __str__(self):
        return f"{self.city.name} - {self.temperature}°C"
    
    def is_cache_valid(self):
        """Check if cached data is still valid (within 30 minutes)"""
        return timezone.now() - self.cached_at < timedelta(minutes=30)

class ForecastData(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='forecast_data')
    forecast_date = models.DateTimeField()
    temperature_min = models.FloatField()
    temperature_max = models.FloatField()
    temperature_day = models.FloatField()
    temperature_night = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.FloatField()
    weather_main = models.CharField(max_length=50)
    weather_description = models.CharField(max_length=100)
    weather_icon = models.CharField(max_length=10)
    wind_speed = models.FloatField()
    wind_direction = models.IntegerField()
    cached_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['city', 'forecast_date']
        ordering = ['forecast_date']
    
    def __str__(self):
        return f"{self.city.name} - {self.forecast_date.date()}"
    
    def is_cache_valid(self):
        """Check if cached forecast data is still valid (within 30 minutes)"""
        return timezone.now() - self.cached_at < timedelta(minutes=30)

class UserPreference(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    favorite_cities = models.ManyToManyField(City, blank=True)
    temperature_unit = models.CharField(
        max_length=1, 
        choices=[('C', 'Celsius'), ('F', 'Fahrenheit')], 
        default='C'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Preferences for {self.session_key}"
