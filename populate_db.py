#!/usr/bin/env python
import os
import django
from django.conf import settings
from datetime import datetime, timedelta
import random

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_backend.settings')
django.setup()

from weather.models import City, WeatherData, ForecastData, UserPreference
from django.utils import timezone

def create_sample_cities():
    """Create sample cities"""
    cities_data = [
        {"name": "London", "country_code": "GB", "latitude": 51.5074, "longitude": -0.1278},
        {"name": "New York", "country_code": "US", "latitude": 40.7128, "longitude": -74.0060},
        {"name": "Tokyo", "country_code": "JP", "latitude": 35.6762, "longitude": 139.6503},
        {"name": "Paris", "country_code": "FR", "latitude": 48.8566, "longitude": 2.3522},
        {"name": "Sydney", "country_code": "AU", "latitude": -33.8688, "longitude": 151.2093},
        {"name": "Mumbai", "country_code": "IN", "latitude": 19.0760, "longitude": 72.8777},
        {"name": "Cairo", "country_code": "EG", "latitude": 30.0444, "longitude": 31.2357},
        {"name": "São Paulo", "country_code": "BR", "latitude": -23.5505, "longitude": -46.6333},
    ]
    
    created_cities = []
    for city_data in cities_data:
        city, created = City.objects.get_or_create(
            name=city_data["name"],
            country_code=city_data["country_code"],
            defaults={
                "latitude": city_data["latitude"],
                "longitude": city_data["longitude"]
            }
        )
        if created:
            print(f"✅ Created city: {city.name}, {city.country_code}")
        else:
            print(f"ℹ️ City already exists: {city.name}, {city.country_code}")
        created_cities.append(city)
    
    return created_cities

def create_sample_weather_data(cities):
    """Create sample weather data for cities"""
    weather_conditions = [
        {"main": "Clear", "description": "clear sky", "icon": "01d"},
        {"main": "Clouds", "description": "scattered clouds", "icon": "03d"},
        {"main": "Rain", "description": "light rain", "icon": "10d"},
        {"main": "Snow", "description": "light snow", "icon": "13d"},
        {"main": "Thunderstorm", "description": "thunderstorm", "icon": "11d"},
    ]
    
    for city in cities:
        # Create current weather data
        weather_condition = random.choice(weather_conditions)
        temperature = round(random.uniform(-10, 35), 1)
        
        weather_data, created = WeatherData.objects.get_or_create(
            city=city,
            defaults={
                "temperature": temperature,
                "feels_like": round(temperature + random.uniform(-3, 3), 1),
                "humidity": random.randint(30, 90),
                "pressure": round(random.uniform(980, 1030), 1),
                "weather_main": weather_condition["main"],
                "weather_description": weather_condition["description"],
                "weather_icon": weather_condition["icon"],
                "wind_speed": round(random.uniform(0, 25), 1),
                "wind_direction": random.randint(0, 360),
                "visibility": random.randint(5000, 10000),
                "uv_index": round(random.uniform(0, 10), 1),
            }
        )
        
        if created:
            print(f"✅ Created weather data for {city.name}: {temperature}°C, {weather_condition['main']}")
        else:
            print(f"ℹ️ Weather data already exists for {city.name}")

def create_sample_forecast_data(cities):
    """Create sample forecast data for cities"""
    weather_conditions = [
        {"main": "Clear", "description": "clear sky", "icon": "01d"},
        {"main": "Clouds", "description": "scattered clouds", "icon": "03d"},
        {"main": "Rain", "description": "light rain", "icon": "10d"},
        {"main": "Snow", "description": "light snow", "icon": "13d"},
    ]
    
    for city in cities:
        # Create 5-day forecast
        for i in range(1, 6):
            forecast_date = timezone.now() + timedelta(days=i)
            weather_condition = random.choice(weather_conditions)
            temp_min = round(random.uniform(-5, 25), 1)
            temp_max = round(temp_min + random.uniform(5, 15), 1)
            
            forecast_data, created = ForecastData.objects.get_or_create(
                city=city,
                forecast_date=forecast_date,
                defaults={
                    "temperature_min": temp_min,
                    "temperature_max": temp_max,
                    "temperature_day": round((temp_min + temp_max) / 2, 1),
                    "temperature_night": round(temp_min + random.uniform(0, 3), 1),
                    "humidity": random.randint(40, 85),
                    "pressure": round(random.uniform(980, 1030), 1),
                    "weather_main": weather_condition["main"],
                    "weather_description": weather_condition["description"],
                    "weather_icon": weather_condition["icon"],
                    "wind_speed": round(random.uniform(0, 20), 1),
                    "wind_direction": random.randint(0, 360),
                }
            )
            
            if created:
                print(f"✅ Created forecast for {city.name} on {forecast_date.date()}: {temp_min}°C to {temp_max}°C")
            else:
                print(f"ℹ️ Forecast already exists for {city.name} on {forecast_date.date()}")

def create_sample_user_preferences():
    """Create sample user preferences"""
    # Create a sample session preference
    session_key = "sample_session_123"
    
    preference, created = UserPreference.objects.get_or_create(
        session_key=session_key,
        defaults={
            "temperature_unit": "C"
        }
    )
    
    if created:
        print(f"✅ Created user preferences for session: {session_key}")
    else:
        print(f"ℹ️ User preferences already exist for session: {session_key}")
    
    # Add some favorite cities
    cities = City.objects.all()[:3]  # First 3 cities as favorites
    preference.favorite_cities.set(cities)
    print(f"✅ Added {cities.count()} cities to favorites")

def main():
    print("🌤️ Populating Weather API Database with Sample Data...")
    print("=" * 60)
    
    try:
        # Create sample cities
        print("\n🏙️ Creating sample cities...")
        cities = create_sample_cities()
        
        # Create sample weather data
        print("\n🌤️ Creating sample weather data...")
        create_sample_weather_data(cities)
        
        # Create sample forecast data
        print("\n📅 Creating sample forecast data...")
        create_sample_forecast_data(cities)
        
        # Create sample user preferences
        print("\n👤 Creating sample user preferences...")
        create_sample_user_preferences()
        
        print("\n" + "=" * 60)
        print("✅ Database population completed successfully!")
        
        # Show final counts
        print(f"\n📊 Final Database Counts:")
        print(f"   Cities: {City.objects.count()}")
        print(f"   Weather Data: {WeatherData.objects.count()}")
        print(f"   Forecast Data: {ForecastData.objects.count()}")
        print(f"   User Preferences: {UserPreference.objects.count()}")
        
        print(f"\n🚀 Your API endpoints should now return data!")
        print(f"   Test with: GET http://localhost:8000/api/cities/")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
