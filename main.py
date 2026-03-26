import requests
import json 
import plotly.graph_objects 


# Obtaining Correct Data from API
def get_correct_race():
    while True:
        country = input("Which Grand Prix would you like to see? (e.g. Australian, Monaco, etc.) ")
        year = input("Which year would you like to see? (e.g. 2025) ")
        session_type = input("Which session would you like to see? (e.g. Qualifying, Race, etc.) ")    

        try:
            response = requests.get(
                    "https://api.openf1.org/v1/sessions",
                    params={
                        "country_name": country,
                        "year": year,
                        "session_name": session_type
                    }
                )
            response.raise_for_status()  # Catches HTTP errors (e.g. 404, 500)
            data = response.json()

            if not data:
                print(f"No session found for {country} Grand Prix in {year} during {session_type}. Please try again.")
                continue # Reiterate function and skip rest of the code.
            
            print(data)
            session = data[0] # As this only returns one session, we know it will be the first in the list.
            session_key = session['session_key']
            print(f"\nFound: {session['country_name']} {session['year']} — {session['session_type']} | Session Key: {session_key}")
            return session_key

        except requests.exceptions.ConnectionError:
            print("Network error: Unable to connect to the API. Please check your internet connection and try again.")
        except requests.exceptions.HTTPError:
            print(f"HTTP error: {response.status_code} - {response.reason}. Please check your input and try again.")
        except Exception as e:
            print(f"An error occured: {e}. Please try again.")


def get_drivers(session_key):
    response = requests.get(f'https://api.openf1.org/v1/drivers?session_key={session_key}')
    driver_info = response.json() 

    drivers = []
    for driver in driver_info:
        drivers.append({
            "driver_number": driver.get("driver_number"), # GET is used instead of [] for safety
            "name": driver.get("full_name"),
            "team_colour": f"#{driver.get('team_colour')}"  # API returns hex without #
        })
    return drivers


def get_lap_times(session_key):
    
    response = requests.get(f"")



SESSION_KEY = get_correct_race()
DRIVERS = get_drivers(SESSION_KEY)
LAP_TIMES = get_lap_times(SESSION_KEY)




