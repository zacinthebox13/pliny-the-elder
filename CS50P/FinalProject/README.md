# Windows and Weather
# CS50P Final Project Submission
#### Demonstration of the program:  <URL HERE>
### Why this program:
Have you ever ended up in that "angry dad mode" because you accidentally left your windows open and now your A/C is cooling down the neighborhood? Who hasn't?

This Windows and Weather program provides a well-needed cure for the angry dad mode by notifying the user, both in the console and via text message, that they need to open or close the windows in their house. Simple summary: It takes in user inputs for their location, desired home temperature, frequency of checking the weather, and phone number - and the program does the rest. No longer do you need to stress and worry about whether you are dumping glorious cold air straight out your windows!

### Files included:
The program includes the following files:

>*weather_windows.py*

Main script for monitoring weather and notifying user to open/close windows

>*test_weather_windows.py*

Testing of *weather_windows.py* utilizing Pytest

>*README.md*

You are here! :wave:

>*requirements.txt*

List of pip-installable libraries required for *weather_windows.py*, listed one per line

### Things to note & areas to improve upon:

This program is only designed to run in the United States as it currently takes in a city & state, and the error-checking is designed for city/state combinations in the US. The API's utilized are not restricted to the U.S. and some additional error handling could be implemented in order to widen the regional application of the program.

The program is currently designed to be used during the summer months and shoulder seasons when the desire is to keep the windows open when the temperatures are cooler outside than inside in order to aid in reducing the amount of time the user's air conditioning is running. It is not currently designed to run during the winter months when it would be advantageous to open your windows while the temperatures are hotter outside than inside in order to reduce the amount of time one's furnace is running, but some simple logic switching and/or the addition of a user's input to indicate if they are running it during summer/winter could be added to make the program's application be year-round.

There are some areas of the code that could be improved upon by extracting some parts of the code and turning them into helper functions to reduce the amount of repeated code currently present in the main function.

### Features:

- Retrieve geographic and weather data using APIs.

- Customizable checking frequency and temperature threshold.

- SMS notifications for temperature updates.

- User-friendly CLI for setup and configuration.


### Setting it up:

There are a few things the user must do before running the program.

**Storing local env variables**

The following environment variables must be set in order for the program to run:

>TWILIO_ACT_SID

Represents the account id of the [Twilio](https://www.twilio.com/en-us) user

>TWILIO_AUTH_TOKEN

Represents the authorization token of the [Twilio](https://www.twilio.com/en-us) user

>TWILIO_PHONE

Represents the sender phone number associated with the [Twilio](https://www.twilio.com/en-us) user's account

>GEOAPIFY_KEY

Represents the API key of the [Geoapify](https://www.geoapify.com/) user

**Dependencies**

The following must be installed/available:

>requests

>time

>os

>twilio

Ensure you have Python 3.x installed on your system. You can download it from [here](https://www.python.org/downloads/) .


### How it works

*weather_windows.py* prompts the user for some initial information for use in checking the weather in a given location, the desired internal home temperature, the frequency the user would like the weather to be checked, and the user's phone number where they would like a notification sent. There are 5 custom functions built into *weather_windows.py* from which the main function calls:

>get_location_input()

**Description**

Prompts the user to input their geographical location in a "City, State" format and performs validation on the input.

**Parameters**

None

**Returns**

location_input (str): A validated string in the format "City, State".

>get_home_temp()

**Description**

Prompts the user to input their desired house temperature (in Fahrenheit) and validates the input.

**Parameters**

None

**Returns**

home_temp (int): A positive integer representing the desired house temperature.

>get_frequency()

**Description**

Prompts the user to input the frequency (in minutes) at which the temperature should be checked and validates the input.

**Parameters**

None

**Returns**

frequency (int): A positive integer representing the check frequency in minutes.

>get_phone_number()

**Description**

Prompts the user to input their phone number (for receiving notifications) and validates the input.

**Parameters**

None

**Returns**

phone_number (str): A validated string representing a 10-digit phone number.

>get_geo_data

**Description**

Fetches geographical data, including longitude and latitude, from the Geoapify API based on the provided city and state.

**Parameters**

city (str): Name of the city.

state (str): Name or abbreviation of the state.

api_key (str): API key for Geoapify API.

**Returns**

resp.json() (dict): A dictionary containing the response data from the Geoapify API.

### Exiting the program

Currently, while in the sleep/wake loop there is no clean 'exit' without user input. The user can input Ctrl + C to quit the program.

### Troubleshooting

- Ensure all environment variables are set correctly.
- Make sure your API accounts are set up properly and active, and the API keys associated with each one is valid and active.
- Check that the provided phone number is verified on Twilio.
- Ensure you have a stable internet connection for accurate data pulls from the API's
