#!/usr/bin/env python
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_backend.settings')

try:
    import django
    django.setup()
    print("✅ Django setup successful!")
    
    # Try to import models
    from weather.models import City, WeatherData, ForecastData
    print("✅ Models imported successfully!")
    
    # Check database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
    
    # Check if tables exist
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name IN ('weather_city', 'weather_weatherdata', 'weather_forecastdata')
    """)
    tables = cursor.fetchall()
    print(f"✅ Found {len(tables)} tables: {[table[0] for table in tables]}")
    
    # Try to create a simple city
    city = City.objects.create(
        name="Test City",
        country_code="TC"
    )
    print(f"✅ Created test city: {city.name}, {city.country_code}")
    
    # Clean up
    city.delete()
    print("✅ Test city deleted successfully!")
    
    print("\n🎉 All tests passed! Your Django setup is working correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
