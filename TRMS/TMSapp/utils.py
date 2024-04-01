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
