from django.conf import settings
import requests
from django.core.cache import cache
#from .models import RoadCondition, Route

def fetch_routes(origin, destination, api_key):
    # Example using Mapbox Directions API
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{origin};{destination}"
    params = {
        "access_token": api_key,
        "geometries": "geojson"
    }  
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # This will raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching routes: {e}")
        return None
    
    
def fetch_weather(location, api_key):
    # Example using OpenWeatherMap API
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": settings.OPENWEATHER_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return None

def fetch_weather_for_route(route_id):
    from .models import Route
    # Example: Fetch weather for the destination of the route
    # Let's assume 'route' has 'end_location' attribute
    route = Route.objects.get(id=route_id)
    end_location = route.end_location  # Assuming this is a string like 'City, Country'

    weather_api_url = "http://api.openweathermap.org/data/2.5/weather"
    
    response = requests.get(weather_api_url, params={"q": end_location, "appid": "your_openweather_api_key"})
    data = response.json()

    # Simplify the data structure for this example; you'll need to adjust based on the actual API response
    return data['weather'][0]['main']  # e.g., 'Rain', 'Sunny'
def fetch_road_condition_for_route(route_id):
    from .models import RoadCondition  # Local import

    # Example: Fetch road condition from your database
    try:
        road_condition = RoadCondition.objects.get(route_id=route_id)
        return road_condition.status  # Assuming 'status' is a field that describes the road condition
    except RoadCondition.DoesNotExist:
        return "Unknown"

def calculate_route_score(route, weather, road_condition):
    score = 0

    # Example scoring logic
    # Decrease score for shorter routes (assuming route.distance is defined)
    score -= route.distance

    # Adjust score based on weather conditions
    if weather == "Rain":
        score += 20  # Bad weather increases the score (worse)
    elif weather == "Sunny":
        score -= 10  # Good weather decreases the score (better)

    # Adjust score based on road conditions
    if road_condition == "Poor":
        score += 30
    elif road_condition == "Good":
        score -= 20

    return score
def parse_weather_response(response_data):
    if 'weather' in response_data and response_data['weather']:
        return response_data['weather'][0]['main']
    else:
        print("Unexpected response format.")
        return None
def get_weather(location):
    cache_key = f'weather_{location}'
    cached_weather = cache.get(cache_key)
    if cached_weather is None:
        weather_data = fetch_weather(location)
        cache.set(cache_key, weather_data, timeout=3600)  # Cache for 1 hour
        return weather_data
    else:
        return cached_weather
def calculate_route_score(route, weather, road_condition):
    """
    Calculates a score for a given route based on distance, weather, and road condition.

    :param route: Route object containing information about the route.
    :param weather: Weather object containing weather conditions for the route.
    :param road_condition: RoadCondition object containing road conditions for the route.
    :return: A numerical score representing the desirability of the route.
    """
    # Base score is the distance - shorter routes are preferred
    score = route.distance

    # Adjust score based on weather conditions
    if weather.condition == 'Good':
        score -= 10  # Subtract points for good weather
    elif weather.condition == 'Bad':
        score += 15  # Add points for bad weather

    # Adjust score based on road conditions
    if road_condition.condition == 'Good':
        score -= 10  # Subtract points for good road conditions
    elif road_condition.condition == 'Bad':
        score += 20  # Add points for bad road conditions

    return score
# this is testing for routes


def get_route_now(api_key, start_point, end_point, **kwargs):
    url = f"https://api.geoapify.com/v1/routing?waypoints={start_point};{end_point}&apiKey={api_key}"
    response = requests.get(url, params=kwargs)
    return response.json()
