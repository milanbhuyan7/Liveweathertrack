#!/usr/bin/env python
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_backend.settings')
django.setup()

from django.db import connection
from weather.models import City, WeatherData, ForecastData, UserPreference

def test_database():
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful!")
        
        # Check if tables exist
        print("\n📊 Checking database tables...")
        
        # Count records in each table
        city_count = City.objects.count()
        weather_count = WeatherData.objects.count()
        forecast_count = ForecastData.objects.count()
        preference_count = UserPreference.objects.count()
        
        print(f"   Cities: {city_count}")
        print(f"   Weather Data: {weather_count}")
        print(f"   Forecast Data: {forecast_count}")
        print(f"   User Preferences: {preference_count}")
        
        # Show sample data if exists
        if city_count > 0:
            print("\n🏙️ Sample Cities:")
            for city in City.objects.all()[:3]:
                print(f"   - {city.name}, {city.country_code}")
        
        if weather_count > 0:
            print("\n🌤️ Sample Weather Data:")
            for weather in WeatherData.objects.all()[:3]:
                print(f"   - {weather.city.name}: {weather.temperature}°C, {weather.weather_main}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_api_endpoints():
    print("\n🔗 Testing API endpoints...")
    
    # Test cities endpoint
    try:
        cities = City.objects.all()
        print(f"   GET /api/cities/ - Found {cities.count()} cities")
    except Exception as e:
        print(f"   ❌ Cities endpoint error: {e}")
    
    # Test weather endpoint
    try:
        weather_data = WeatherData.objects.all()
        print(f"   GET /api/weather/ - Found {weather_data.count()} weather records")
    except Exception as e:
        print(f"   ❌ Weather endpoint error: {e}")

if __name__ == "__main__":
    print("🔍 Testing Weather API Database Connection...")
    print("=" * 50)
    
    if test_database():
        test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
