from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
from .models import City, WeatherData, ForecastData, UserPreference
from .serializers import (
    CitySerializer, WeatherDataSerializer, ForecastDataSerializer,
    UserPreferenceSerializer, AddCitySerializer
)
from .services import WeatherCacheService, WeatherAPIException

logger = logging.getLogger('weather_api')

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    
    def create(self, request):
        """Add a new city with enhanced error handling"""
        serializer = AddCitySerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            country_code = serializer.validated_data['country_code']
            
            logger.info(f"Attempting to add city: {name}, {country_code}")
            
            # Check if city already exists
            city, created = City.objects.get_or_create(
                name__iexact=name,
                country_code=country_code,
                defaults={'name': name, 'country_code': country_code}
            )
            
            if created:
                # Try to fetch weather data to validate the city
                try:
                    weather_service = WeatherCacheService()
                    weather_service.get_or_fetch_current_weather(city)
                    logger.info(f"Successfully added and validated city: {name}, {country_code}")
                except WeatherAPIException as e:
                    logger.error(f"Failed to validate city {name}, {country_code}: {e}")
                    city.delete()
                    
                    if "not found" in str(e).lower():
                        return Response(
                            {'error': f'City "{name}" not found in {country_code}. Please check the spelling and country code.'}, 
                            status=status.HTTP_404_NOT_FOUND
                        )
                    elif "api key" in str(e).lower():
                        return Response(
                            {'error': 'Weather service configuration error. Please try again later.'}, 
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
                    elif "rate limit" in str(e).lower():
                        return Response(
                            {'error': 'Too many requests. Please wait a moment and try again.'}, 
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
                    else:
                        return Response(
                            {'error': f'Unable to fetch weather data: {str(e)}'}, 
                            status=status.HTTP_503_SERVICE_UNAVAILABLE
                        )
                except Exception as e:
                    logger.error(f"Unexpected error validating city {name}, {country_code}: {e}")
                    city.delete()
                    return Response(
                        {'error': 'An unexpected error occurred. Please try again.'}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.info(f"City already exists: {name}, {country_code}")
            
            return Response(CitySerializer(city).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete city and invalidate its cache"""
        city = self.get_object()
        city_id = city.id
        city_name = f"{city.name}, {city.country_code}"
        
        # Invalidate cache before deletion
        weather_service = WeatherCacheService()
        weather_service.invalidate_city_cache(city_id)
        
        logger.info(f"Deleting city: {city_name}")
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def weather(self, request, pk=None):
        """Get current weather for a city with enhanced error handling"""
        city = get_object_or_404(City, pk=pk)
        
        try:
            weather_service = WeatherCacheService()
            weather_data = weather_service.get_or_fetch_current_weather(city)
            serializer = WeatherDataSerializer(weather_data)
            return Response(serializer.data)
        except WeatherAPIException as e:
            logger.error(f"Weather API error for city {city.name}: {e}")
            if "not found" in str(e).lower():
                return Response(
                    {'error': f'Weather data not available for {city.name}', 'code': 'CITY_NOT_FOUND'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                return Response(
                    {'error': 'Weather service is temporarily unavailable. Please try again.', 'code': 'SERVICE_UNAVAILABLE'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            else:
                return Response(
                    {'error': f'Failed to get weather data: {str(e)}', 'code': 'API_ERROR'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            logger.error(f"Unexpected error getting weather for city {city.name}: {e}")
            return Response(
                {'error': 'An unexpected error occurred', 'code': 'INTERNAL_ERROR'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def forecast(self, request, pk=None):
        """Get 5-day forecast for a city with enhanced error handling"""
        city = get_object_or_404(City, pk=pk)
        
        try:
            weather_service = WeatherCacheService()
            forecast_data = weather_service.get_or_fetch_forecast(city)
            serializer = ForecastDataSerializer(forecast_data, many=True)
            return Response(serializer.data)
        except WeatherAPIException as e:
            logger.error(f"Forecast API error for city {city.name}: {e}")
            if "not found" in str(e).lower():
                return Response(
                    {'error': f'Forecast data not available for {city.name}', 'code': 'CITY_NOT_FOUND'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            elif "timeout" in str(e).lower() or "connection" in str(e).lower():
                return Response(
                    {'error': 'Weather service is temporarily unavailable. Please try again.', 'code': 'SERVICE_UNAVAILABLE'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            else:
                return Response(
                    {'error': f'Failed to get forecast data: {str(e)}', 'code': 'API_ERROR'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
        except Exception as e:
            logger.error(f"Unexpected error getting forecast for city {city.name}: {e}")
            return Response(
                {'error': 'An unexpected error occurred', 'code': 'INTERNAL_ERROR'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer
    
    def get_queryset(self):
        """Filter weather data by city if specified"""
        queryset = WeatherData.objects.all()
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset

class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ForecastData.objects.all()
    serializer_class = ForecastDataSerializer
    
    def get_queryset(self):
        """Filter forecast data by city if specified"""
        queryset = ForecastData.objects.all()
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset

class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer
    
    def get_queryset(self):
        """Get preferences for current session"""
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        
        return UserPreference.objects.filter(session_key=session_key)
    
    def create(self, request):
        """Create or update user preferences with error handling"""
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = self.request.session.session_key
        
        try:
            preference, created = UserPreference.objects.get_or_create(
                session_key=session_key,
                defaults={'temperature_unit': request.data.get('temperature_unit', 'C')}
            )
            
            if not created:
                # Update existing preference
                serializer = UserPreferenceSerializer(preference, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    logger.info(f"Updated preferences for session {session_key}")
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = UserPreferenceSerializer(preference)
            logger.info(f"Created preferences for session {session_key}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error managing preferences for session {session_key}: {e}")
            return Response(
                {'error': 'Failed to save preferences'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def add_favorite_city(self, request):
        """Add a city to favorites with error handling"""
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = self.request.session.session_key
        
        city_id = request.data.get('city_id')
        if not city_id:
            return Response({'error': 'city_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            city = City.objects.get(id=city_id)
            preference, created = UserPreference.objects.get_or_create(session_key=session_key)
            
            if city in preference.favorite_cities.all():
                return Response({'message': 'City is already in favorites'}, status=status.HTTP_200_OK)
            
            preference.favorite_cities.add(city)
            logger.info(f"Added city {city.name} to favorites for session {session_key}")
            
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding favorite city for session {session_key}: {e}")
            return Response(
                {'error': 'Failed to add city to favorites'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def remove_favorite_city(self, request):
        """Remove a city from favorites with error handling"""
        session_key = request.session.session_key
        if not session_key:
            return Response({'error': 'No session found'}, status=status.HTTP_400_BAD_REQUEST)
        
        city_id = request.data.get('city_id')
        if not city_id:
            return Response({'error': 'city_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            city = City.objects.get(id=city_id)
            preference = UserPreference.objects.get(session_key=session_key)
            preference.favorite_cities.remove(city)
            logger.info(f"Removed city {city.name} from favorites for session {session_key}")
            
            serializer = UserPreferenceSerializer(preference)
            return Response(serializer.data)
        except (City.DoesNotExist, UserPreference.DoesNotExist):
            return Response({'error': 'City or preference not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error removing favorite city for session {session_key}: {e}")
            return Response(
                {'error': 'Failed to remove city from favorites'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
