
# import the necessary libraries/modules

import requests, time, os, twilio
from requests.structures import CaseInsensitiveDict
from twilio.rest import Client

# define a function that will ask the user for their location
def get_location_input():
    while True:
        location_input = input("What city & state are you located in? Please provide in the format of City, State (2-letter state abbreviation): ")
        if ',' not in location_input:
            print('Invalid location. Please try again and ensure a city and state are provided with a comma separating the two values.')
            continue
        parts = location_input.split(", ")
        if len(parts) != 2:
            print('Invalid location. Input must contain a city, followed by a comma and a space, and then a state abbreviation. Please try again.')
            continue
        city, state = parts
        if not city or not state:
            print('Both a city and state must be provided. Please input your location again.')
            continue
        if len(state) != 2:
            print('Invalid state abbreviation. Please input your location again.')
            continue
        else:
            return location_input

# define a function that will ask the user for their desired house temperature
def get_home_temp():
    while True:
        home_temp_input = input("What is your desired house temperature (positive integer in Fahrenheit): ")
        if home_temp_input.isdigit():
            home_temp = int(home_temp_input)
            if home_temp > 0:
                return home_temp
            else: 
                print('Invalid temperature. Please try again and ensure a positive integer is provided.')
        else:
            print('Invalid temperature. Please try again and ensure a positive integer is provided.')

# define a function that will ask the user for the frequency of checking the temperature in minutes
def get_frequency():
    while True:
        frequency_input = input('Enter how often would you like to check the temperature? (positive integer in minutes): ')
        if frequency_input.isdigit():
            frequency = int(frequency_input)
            if frequency > 0:
                return frequency
            else: 
                print('Invalid frequency. Please try again and ensure a positive integer is provided.')
        else: 
            print('Invalid frequency. Please try again and ensure a positive integer is provided.')

# define a function that will ask the user for their phone number to receive the notifications
def get_phone_number():
    while True:
        phone_number = input('Enter your phone number to receive notifications (10 digit number): ')
        if len(phone_number) == 10 and phone_number.isdigit():
            return phone_number
        else:
            print('Invalid phone number. Please try again and ensure a 10-digit phone number is provided.')

# define a function that will get the geo data from the API
def get_geo_data(city:str, state:str, api_key:str):
    geo_url = f"https://api.geoapify.com/v1/geocode/search?city={city}&state={state}&format=json&apiKey={api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(geo_url, headers=headers)

    return resp.json()

# set the api key for the geo data
api_key = os.environ.get('GEOAPIFY_KEY')

# set the variables for the twilio account
account_sid = os.environ.get('TWILIO_ACT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
sender_phone_number = '+18556436461'
client = Client(account_sid, auth_token)

# set the first check value to None
outside_temp_greaterthan_inside = None

# prompt the user for their location
user_input = get_location_input()

# prompt the user for their desired house temperature
home_temp = int(get_home_temp())

# prompt the user for the frequency of checking the temperature
frequency = int(get_frequency())
frequency_seconds = frequency * 60

# prompt the user for their phone number to receive the notifications
phone_number = f'+1{get_phone_number()}'

# convert the provided location into city and state
city, state = user_input.split(", ")

# convert the city and state into longitude and latitude
geo_data = get_geo_data(city, state, api_key)

# error-checking to ensure a proper location is provided, re-prompt if not
while not geo_data.get('results'):
    print("Location not found. Try again.")
    user_input = get_location_input()
    city, state = user_input.split(", ")
    geo_data = get_geo_data(city, state, api_key)

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
    if frequency == 1:
        print(f"I will check again in {frequency} minute.")
    else: print(f"I will check again in {frequency} minutes.")
else:
    print(f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Open your windows to help cool your house down to under {home_temp} degrees!')
    if frequency == 1:
        print(f"I will check again in {frequency} minute.")
    else: print(f"I will check again in {frequency} minutes.")

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
        message = client.messages.create(
            to= phone_number,
            from_=sender_phone_number,
            body=f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Open your windows to help cool your house down to under {home_temp} degrees!'
        )
        print(f'A threshold change was detected and notification sent as a reminder to open your windows. It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}.')
        if frequency == 1:
            print(f'Checking again in {frequency} minute.')
        else: print(f'Checking again in {frequency} minutes.')
    elif not outside_temp_greaterthan_inside and current_outside_temp_greaterthan_inside:
        message = client.messages.create(
            to=phone_number,
            from_=sender_phone_number,
            body=f'It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Close your windows to stop your house from going over {home_temp} degrees!'
        )
        print(f'A threshold change was detected and notification sent as a reminder to close your windows. It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}.')
        if frequency == 1:
            print(f'Checking again in {frequency} minute.')
        else: print(f'Checking again in {frequency} minutes.')
    else:
        if frequency == 1:
            print(f'The temperature threshold change has not been met - no further action is needed. It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Checking again in {frequency} minute.')
        else: print(f'The temperature threshold change has not been met - no further action is needed. It is currently {current_temperature} degrees Fahrenheit outside in {city}, {state}. Checking again in {frequency} minutes.')

    # update the prior check result
    outside_temp_greaterthan_inside = current_outside_temp_greaterthan_inside