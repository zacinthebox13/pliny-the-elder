
# import the necessary libraries/modules

import requests, time, json, os
from requests.structures import CaseInsensitiveDict

# define a function that will ask the user for their location
def get_location_input():
    return input("What city & state are you located in? Please provide in the format of City, State (2-letter state abbreviation): ")

# define a function that will ask the user for their desired house temperature
def get_home_temp():
    return input("What is your desired house temperature (2-digit integer in Fahrenheit): ")

# define a function that will ask the user for the frequency of checking the temperature in minutes
def get_frequency():
    return input('Enter how often would you like to check the temperature? (in minutes): ')

# define a function that will get the geo data from the API
def get_geo_data(city, state, api_key):
    geo_url = f"https://api.geoapify.com/v1/geocode/search?city={city}&state={state}&format=json&apiKey={api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(geo_url, headers=headers)

    return resp.json()

# set the api key for the geo data
api_key = os.environ.get('GEOAPIFY_KEY')

# set the prior check result
outside_temp_greaterthan_inside = None

# prompt the user for their location
user_input = get_location_input()

# prompt the user for their desired house temperature
home_temp = get_home_temp()
home_temp = int(home_temp)

# prompt the user for the frequency of checking the temperature
frequency = get_frequency()
frequency = int(frequency)
frequency_seconds = frequency * 60

# convert the provided location into city and state
city, state = user_input.split(", ")

# convert the city and state into longitude and latitude
geo_data = get_geo_data(city, state, api_key)

# error-checking to ensure a proper location is provided, re-prompt if not
while not geo_data['results']:
    print("Location not found. Try again.")
    user_input = get_location_input()
    city, state = user_input.split(", ")
    geo_data = get_geo_data(city, state)

# extract the longitude, latitude, and timezone from the geo data
lon = geo_data["results"][0]["lon"]
lat = geo_data["results"][0]["lat"]
timezone_location = geo_data["results"][0]["timezone"]["name"]
timezone_country, timezone_state = timezone_location.split("/")

# use the longitude, latitude, and timezone to get the current temperature
weather_api = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True&temperature_unit=fahrenheit&windspeed_unit=mph&timezone={timezone_country}%2F{timezone_state}&"
response = requests.get(weather_api)

# error-checking to ensure the API is responding
if response.status_code == 200:
    data = response.json()
    current_temperature = data["current_weather"]["temperature"]
    outside_temp_greaterthan_inside = current_temperature > home_temp
else:
    print("Error. API not responding. Please try again later.")
    exit()

# initial check to see if the temperature is above or below the user input
if outside_temp_greaterthan_inside:
    print(f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Close your windows to stop your house from going over {home_temp} degrees!')
    print(f"I will check again in {frequency} minute(s).")
else:
    print(f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Open your windows to help cool your house down to under {home_temp} degrees!')
    print(f"I will check again in {frequency} minute(s).")

#loop for checking the temperature every x minutes
while True:
    
    # setting the amount of time to sleep between checks
    time.sleep(frequency_seconds)
    
    response = requests.get(weather_api)

    print('Checking again...')

    # error-checking to ensure the API is responding
    if response.status_code == 200:
        data = response.json()
        current_temperature = data["current_weather"]["temperature"]
    
    else:
        print("Error. API not responding. Please try again later.")
        continue

    # extract the current temperature from the weather data
    current_temperature = data["current_weather"]["temperature"]

    # when the temperature detected is above or below the user input, remind the user to open/close the windows in the house
    current_outside_temp_greaterthan_inside = current_temperature > home_temp
    
    if outside_temp_greaterthan_inside and not current_outside_temp_greaterthan_inside:
        print(f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Open your windows to help cool your house down to under {home_temp} degrees!')
    elif not outside_temp_greaterthan_inside and current_outside_temp_greaterthan_inside:
        print(f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Close your windows to stop your house from going over {home_temp} degrees!')
    else:
        print(f'The temperature threshold change has not been met - no further action is needed. Checking again in {frequency} minute(s).')

    # update the prior check result
    outside_temp_greaterthan_inside = current_outside_temp_greaterthan_inside