import pytest
from weather_windows import validate_get_location_input, validate_get_frequency, validate_get_phone_number, validate_get_home_temp

def main():
    test_location()
    test_frequency()
    test_phone_number()
    test_home_temp()

def test_location():
    # valid inputs
    assert validate_get_location_input('Oakland, CA') == ('Oakland', 'CA')
    assert validate_get_location_input('Reno, NV') == ('Reno', 'NV')
    # invalid inputs
    with pytest.raises(ValueError, match='Invalid state abbreviation. Please us a 2-letter state abbreviation.'):
        validate_get_location_input('Banana, Banana')
    with pytest.raises(ValueError, match='Invalid location. Ensure a city and state are provided with a comma separating the two values.'):
        validate_get_location_input('Oakland CA')
    with pytest.raises(ValueError, match='Invalid location'):
        validate_get_location_input('Invalid city input. Please do not add any special characters to the city name.')
    
def test_frequency():
    # valid inputs
    assert validate_get_frequency('1') == 1
    assert validate_get_frequency('2') == 2
    # invalid inputs
    with pytest.raises(ValueError, match='Invalid frequency. Please try again and ensure a positive integer is provided.'):
        validate_get_frequency('thirty')
    with pytest.raises(ValueError, match='Invalid frequency. Please try again and ensure a positive integer is provided.'):
        validate_get_frequency('-1')

def test_phone_number():
    # valid inputs
    assert validate_get_phone_number('1234567890') == '1234567890'
    # invalid inputs
    with pytest.raises(ValueError, match='Invalid phone number. Please try again and ensure a 10-digit phone number is provided.'):
        validate_get_phone_number('123456789')
    with pytest.raises(ValueError, match='Invalid phone number. Please try again and ensure a 10-digit phone number is provided.'):
        validate_get_phone_number('banana')

def test_home_temp():
    # valid inputs
    assert validate_get_home_temp('60') == 60
    # invalid inputs
    with pytest.raises(ValueError, match='Invalid temperature. Please try again and ensure a positive integer is provided.'):
        validate_get_home_temp('sixty')
    with pytest.raises(ValueError, match='Invalid temperature. Please try again and ensure a positive integer is provided.'):
        validate_get_home_temp('-10')