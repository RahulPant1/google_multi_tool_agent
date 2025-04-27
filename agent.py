import datetime
from zoneinfo import ZoneInfo
from google.adk import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "The weather in Tokyo is rainy with a temperature of 18°C."},
        "bengaluru": {"status": "success", "report": f"The weather in Bengaluru is pleasant with a temperature of 30°C. Current time in Bengaluru is {datetime.datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S %Z%z')}"}
    }
    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Weather information for '{city}' is not available."}

def get_current_time(city: str) -> dict:
    """Retrieves the current time for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    print(f"--- Tool: get_current_time called for city: {city} ---")
    try:
        tz_identifier = None
        if city.lower() == "new york":
            tz_identifier = "America/New_York"
        elif city.lower() == "london":
            tz_identifier = "Europe/London"
        elif city.lower() == "tokyo":
            tz_identifier = "Asia/Tokyo"
        elif city.lower() == "bengaluru":
            tz_identifier = "Asia/Kolkata"

        if tz_identifier:
            tz = ZoneInfo(tz_identifier)
            now = datetime.datetime.now(tz)
            report = f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
            return {"status": "success", "report": report}
        else:
            return {"status": "error", "error_message": f"Sorry, I don't have timezone information for {city}."}
    except Exception as e:
        return {"status": "error", "error_message": f"An error occurred: {e}"}

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-1.5-flash",  # Or your preferred Gemini model (ensure access)
    description="Agent to answer questions about the time and weather in a city.",
    instruction="I can answer your questions about the time and weather in a city.",
    tools=[get_weather, get_current_time]
)