
# import the necessary libraries/modules

import requests, time, os, twilio
from requests.structures import CaseInsensitiveDict
from twilio.rest import Client

def main():
    # set the api key for the geo data
    api_key = os.environ.get('GEOAPIFY_KEY')
    if not api_key:
        print("API Key for Geoapify is not set. Please set the environment variable 'GEOAPIFY_KEY'.")
        exit()

    # set the variables for the twilio account
    account_sid = os.environ.get('TWILIO_ACT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    sender_phone_number = os.environ.get('TWILIO_PHONE')
    
    if not account_sid:
        print("Twilio account information is not set. Please set the environment variable 'TWILIO_ACT_SID'.")
        exit()
    elif not auth_token:
        print("Twilio account information is not set. Please set the environment variable 'TWILIO_AUTH_TOKEN'.")
        exit()
    elif not sender_phone_number:
        print("Twilio account information is not set. Please set the environment variable 'TWILIO_PHONE'.")
        exit()

    client = Client(account_sid, auth_token)

    # set the first check value to None
    outside_temp_greaterthan_inside = None

    # prompt the user for their location
    user_input_location = get_location_input()

    # prompt the user for their desired house temperature
    home_temp = int(get_home_temp())

    # prompt the user for the frequency of checking the temperature
    frequency = int(get_frequency())
    frequency_seconds = frequency * 60

    # prompt the user for their phone number to receive the notifications
    phone_number = f'+1{get_phone_number()}'

    # convert the provided location into city and state
    city, state = user_input_location.split(", ")

    # convert the city and state into longitude and latitude
    geo_data = get_geo_data(city, state, api_key)

    # error-checking to ensure a proper location is provided, re-prompt if not
    while not geo_data.get('results'):
        print("Location not found. Try again.")
        user_input_location = get_location_input()
        city, state = user_input_location.split(", ")
        geo_data = get_geo_data(city, state, api_key)

    # extract the longitude, latitude, and timezone from the geo data
    lon = geo_data["results"][0]["lon"]
    lat = geo_data["results"][0]["lat"]
    timezone_location = geo_data["results"][0]["timezone"]["name"]
    timezone_country, timezone_state = timezone_location.split("/")

    # use the longitude, latitude, and timezone to get the current temperature
    weather_api = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True&temperature_unit=fahrenheit&windspeed_unit=mph&timezone={timezone_country}%2F{timezone_state}&"
    response = requests.get(weather_api)

    # error-checking to ensure the API is responding + initial check to see if the temperature is above or below the user input
    if response.status_code == 200:
        data = response.json()
        if "current_weather" in data and "temperature" in data["current_weather"]:
            current_temperature = data["current_weather"]["temperature"]
        else:
            print("Unexpected data from the weather API. Please check the response.")
        outside_temp_greaterthan_inside = current_temperature > home_temp
    else:
        print("Error. API not responding. Please try again later.")
        exit()

    # notify user of the current temperature and whether they should open or close their windows
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
    try:
        while True:
            
            # setting the amount of time to sleep between checks
            time.sleep(frequency_seconds)
            
            response = requests.get(weather_api)

            print('Checking again...')

            # error-checking to ensure the API is responding + get the current temperature
            if response.status_code == 200:
                data = response.json()
                new_temperature = data["current_weather"]["temperature"]
            
            else:
                print("Error. API not responding. Please try again later.")
                continue

            # when the temperature detected is above or below the user input, remind the user to open/close the windows in the house
            current_outside_temp_greaterthan_inside = new_temperature > home_temp
            
            if outside_temp_greaterthan_inside and not current_outside_temp_greaterthan_inside:
                message = client.messages.create(
                    to= phone_number,
                    from_=sender_phone_number,
                    body=f'It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}. Open your windows to help cool your house down to under {home_temp} degrees!'
                )
                print(f'A threshold change was detected and notification sent as a reminder to open your windows. It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}.')
                if frequency == 1:
                    print(f'Checking again in {frequency} minute.')
                else: print(f'Checking again in {frequency} minutes.')
            elif not outside_temp_greaterthan_inside and current_outside_temp_greaterthan_inside:
                message = client.messages.create(
                    to=phone_number,
                    from_=sender_phone_number,
                    body=f'It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}. Close your windows to stop your house from going over {home_temp} degrees!'
                )
                print(f'A threshold change was detected and notification sent as a reminder to close your windows. It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}.')
                if frequency == 1:
                    print(f'Checking again in {frequency} minute.')
                else: print(f'Checking again in {frequency} minutes.')
            else:
                if frequency == 1:
                    print(f'The temperature threshold change has not been met - no further action is needed. It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}. Checking again in {frequency} minute.')
                else: print(f'The temperature threshold change has not been met - no further action is needed. It is currently {new_temperature} degrees Fahrenheit outside in {city}, {state}. Checking again in {frequency} minutes.')

            # update the prior check result
            outside_temp_greaterthan_inside = current_outside_temp_greaterthan_inside
    except KeyboardInterrupt:
        print('\nUser requested to exit. Exiting...')



# define a function that will ask the user for their location
def get_location_input():
    while True:
        location_input = input("What city & state are you located in? Please provide in the format of City, State (2-letter state abbreviation): ")
        try:
            validate_get_location_input(location_input)
            return location_input
        except ValueError as error_message:
            print(error_message)
        
def validate_get_location_input(location_input):
    if ',' not in location_input:
        raise ValueError('Invalid location. Ensure a city and state are provided with a comma separating the two values.')
    
    parts = location_input.split(", ")

    if len(parts) != 2:
        raise ValueError('Invalid location. Input must contain a city, followed by a comma and a space, and then a state abbreviation.')
    
    city, state = parts

    if not city or not state:
        raise ValueError('Both a city and state must be provided.')
    if len(state) != 2 or not state.isalpha():
        raise ValueError('Invalid state abbreviation. Please us a 2-letter state abbreviation.')
    if not city.isalpha():
        raise ValueError('Invalid city input. Please do not add any special characters to the city name.')
    
    return city, state

# define a function that will ask the user for their desired house temperature
def get_home_temp():
    while True:
        try:
            home_temp_input = input('What is your desired house temperature? (positive integer in Fahrenheit): ')
            home_temp = validate_get_home_temp(home_temp_input)
            return home_temp
        except ValueError as error_message:
            print(error_message)

def validate_get_home_temp(home_temp_input):
    if not home_temp_input.isdigit():
        raise ValueError('Invalid temperature. Please try again and ensure a positive integer is provided.')
    
    home_temp = int(home_temp_input)

    if home_temp <= 0:
        raise ValueError('Invalid temperature. Please try again and ensure a positive integer is provided.')
    
    return home_temp

# define a function that will ask the user for the frequency of checking the temperature in minutes
def get_frequency():
    while True:
        try:
            frequency_input = input('How often would you like to check the temperature? (positive integer in minutes): ')
            frequency = validate_get_frequency(frequency_input)
            return frequency
        except ValueError as error_message:
            print(error_message)

def validate_get_frequency(frequency_input):
    if not frequency_input.isdigit():
        raise ValueError('Invalid frequency. Please try again and ensure a positive integer is provided.')
    
    frequency = int(frequency_input)

    if frequency <= 0:
        raise ValueError('Invalid frequency. Please try again and ensure a positive integer is provided.')
    
    return frequency

# define a function that will ask the user for their phone number to receive the notifications
def get_phone_number():
    while True:
        try:
            phone_number_input = input('What is your phone number? (10-digit phone number): ')
            phone_number = validate_get_phone_number(phone_number_input)
            return phone_number
        except ValueError as error_message:
            print(error_message)

def validate_get_phone_number(phone_number):
    if len(phone_number) != 10 or not phone_number.isdigit():
        raise ValueError('Invalid phone number. Please try again and ensure a 10-digit phone number is provided.')
    
    return phone_number

# define a function that will get the geo data from the API since the weather API requires lat/lon but we are collecting city/state from the user
def get_geo_data(city:str, state:str, api_key:str):
    geo_url = f"https://api.geoapify.com/v1/geocode/search?city={city}&state={state}&format=json&apiKey={api_key}"

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"

    resp = requests.get(geo_url, headers=headers)

    return resp.json()
   
if __name__ == '__main__':
    main()