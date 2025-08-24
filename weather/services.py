import requests
import logging
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta, timezone as dt_timezone
from .models import City, WeatherData, ForecastData

logger = logging.getLogger('weather_api')

class WeatherAPIException(Exception):
    """Custom exception for weather API errors"""
    pass

class OpenWeatherMapService:
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = settings.OPENWEATHER_BASE_URL
        self.timeout = 10
        self.max_retries = 3
    
    def _make_request(self, url, params, retry_count=0):
        """Make HTTP request with retry logic and error handling"""
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout error for URL: {url}")
            if retry_count < self.max_retries:
                logger.info(f"Retrying request (attempt {retry_count + 1}/{self.max_retries})")
                return self._make_request(url, params, retry_count + 1)
            raise WeatherAPIException("Request timeout after multiple retries")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise WeatherAPIException("City not found")
            elif e.response.status_code == 401:
                raise WeatherAPIException("Invalid API key")
            elif e.response.status_code == 429:
                raise WeatherAPIException("API rate limit exceeded")
            else:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise WeatherAPIException(f"API error: {e.response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for URL: {url}")
            raise WeatherAPIException("Unable to connect to weather service")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise WeatherAPIException("Weather service request failed")
    
    def get_current_weather(self, city_name, country_code):
        """Fetch current weather data from OpenWeatherMap API"""
        url = f"{self.base_url}/weather"
        params = {
            'q': f"{city_name},{country_code}",
            'appid': self.api_key,
            'units': 'metric'
        }
        
        logger.info(f"Fetching current weather for {city_name}, {country_code}")
        return self._make_request(url, params)
    
    def get_forecast(self, city_name, country_code):
        """Fetch 5-day forecast data from OpenWeatherMap API"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': f"{city_name},{country_code}",
            'appid': self.api_key,
            'units': 'metric'
        }
        
        logger.info(f"Fetching forecast for {city_name}, {country_code}")
        return self._make_request(url, params)

class WeatherCacheService:
    def __init__(self):
        self.openweather_service = OpenWeatherMapService()
        self.weather_cache_prefix = "weather_current"
        self.forecast_cache_prefix = "weather_forecast"
    
    def _get_weather_cache_key(self, city_id):
        """Generate cache key for current weather"""
        return f"{self.weather_cache_prefix}_{city_id}"
    
    def _get_forecast_cache_key(self, city_id):
        """Generate cache key for forecast data"""
        return f"{self.forecast_cache_prefix}_{city_id}"
    
    def get_or_fetch_current_weather(self, city):
        """Get current weather from cache or fetch from API if stale"""
        cache_key = self._get_weather_cache_key(city.id)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached weather data for {city.name}")
            return cached_data
        
        # Check database cache
        cached_weather = WeatherData.objects.filter(city=city).first()
        
        if cached_weather and cached_weather.is_cache_valid():
            cache.set(cache_key, cached_weather, settings.WEATHER_CACHE_DURATION)
            logger.info(f"Returning database cached weather data for {city.name}")
            return cached_weather
        
        # Fetch fresh data from API
        try:
            weather_data = self.openweather_service.get_current_weather(
                city.name, city.country_code
            )
            
            # Update city coordinates if not set
            if not city.latitude or not city.longitude:
                city.latitude = weather_data['coord']['lat']
                city.longitude = weather_data['coord']['lon']
                city.save()
                logger.info(f"Updated coordinates for {city.name}")
            
            # Create or update weather data
            weather_obj, created = WeatherData.objects.update_or_create(
                city=city,
                defaults={
                    'temperature': weather_data['main']['temp'],
                    'feels_like': weather_data['main']['feels_like'],
                    'humidity': weather_data['main']['humidity'],
                    'pressure': weather_data['main']['pressure'],
                    'weather_main': weather_data['weather'][0]['main'],
                    'weather_description': weather_data['weather'][0]['description'],
                    'weather_icon': weather_data['weather'][0]['icon'],
                    'wind_speed': weather_data.get('wind', {}).get('speed', 0),
                    'wind_direction': weather_data.get('wind', {}).get('deg', 0),
                    'visibility': weather_data.get('visibility'),
                    'cached_at': timezone.now()
                }
            )
            
            cache.set(cache_key, weather_obj, settings.WEATHER_CACHE_DURATION)
            logger.info(f"Fetched and cached fresh weather data for {city.name}")
            
            return weather_obj
            
        except WeatherAPIException as e:
            logger.error(f"Weather API error for {city.name}: {e}")
            # If API fails and we have old cached data, return it
            if cached_weather:
                logger.info(f"Returning stale cached data for {city.name} due to API error")
                return cached_weather
            raise e
        except Exception as e:
            logger.error(f"Unexpected error fetching weather for {city.name}: {e}")
            if cached_weather:
                return cached_weather
            raise WeatherAPIException("Failed to fetch weather data")
    
    def get_or_fetch_forecast(self, city):
        """Get forecast from cache or fetch from API if stale"""
        cache_key = self._get_forecast_cache_key(city.id)
        
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached forecast data for {city.name}")
            return cached_data
        
        # Check database cache
        cached_forecasts = ForecastData.objects.filter(city=city)
        
        if cached_forecasts.exists() and cached_forecasts.first().is_cache_valid():
            forecast_list = list(cached_forecasts)
            cache.set(cache_key, forecast_list, settings.WEATHER_CACHE_DURATION)
            logger.info(f"Returning database cached forecast data for {city.name}")
            return forecast_list
        
        # Fetch fresh forecast data from API
        try:
            forecast_data = self.openweather_service.get_forecast(
                city.name, city.country_code
            )
            
            # Clear old forecast data
            ForecastData.objects.filter(city=city).delete()
            
            # Process forecast data (group by day and take one forecast per day)
            daily_forecasts = {}
            for item in forecast_data['list']:
                forecast_date = datetime.fromtimestamp(item['dt'], tz=dt_timezone.utc)
                date_key = forecast_date.date()
                
                # Take the first forecast for each day (usually around noon)
                if date_key not in daily_forecasts:
                    daily_forecasts[date_key] = item
            
            # Create forecast objects
            forecast_objects = []
            for date_key, forecast_item in list(daily_forecasts.items())[:5]:  # Limit to 5 days
                forecast_date = datetime.fromtimestamp(forecast_item['dt'], tz=dt_timezone.utc)
                
                forecast_obj = ForecastData.objects.create(
                    city=city,
                    forecast_date=forecast_date,
                    temperature_min=forecast_item['main']['temp_min'],
                    temperature_max=forecast_item['main']['temp_max'],
                    temperature_day=forecast_item['main']['temp'],
                    temperature_night=forecast_item['main']['temp'],  # API doesn't separate day/night in 5-day forecast
                    humidity=forecast_item['main']['humidity'],
                    pressure=forecast_item['main']['pressure'],
                    weather_main=forecast_item['weather'][0]['main'],
                    weather_description=forecast_item['weather'][0]['description'],
                    weather_icon=forecast_item['weather'][0]['icon'],
                    wind_speed=forecast_item.get('wind', {}).get('speed', 0),
                    wind_direction=forecast_item.get('wind', {}).get('deg', 0),
                    cached_at=timezone.now()
                )
                forecast_objects.append(forecast_obj)
            
            cache.set(cache_key, forecast_objects, settings.WEATHER_CACHE_DURATION)
            logger.info(f"Fetched and cached fresh forecast data for {city.name}")
            
            return forecast_objects
            
        except WeatherAPIException as e:
            logger.error(f"Forecast API error for {city.name}: {e}")
            # If API fails and we have old cached data, return it
            if cached_forecasts.exists():
                logger.info(f"Returning stale cached forecast for {city.name} due to API error")
                return list(cached_forecasts)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error fetching forecast for {city.name}: {e}")
            if cached_forecasts.exists():
                return list(cached_forecasts)
            raise WeatherAPIException("Failed to fetch forecast data")
    
    def invalidate_city_cache(self, city_id):
        """Invalidate all cache entries for a specific city"""
        weather_key = self._get_weather_cache_key(city_id)
        forecast_key = self._get_forecast_cache_key(city_id)
        
        cache.delete(weather_key)
        cache.delete(forecast_key)
        logger.info(f"Invalidated cache for city {city_id}")
    
    def clear_all_cache(self):
        """Clear all weather-related cache entries"""
        cache.clear()
        logger.info("Cleared all weather cache")
