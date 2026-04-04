import requests
import plotly.graph_objects as go


# Obtaining Correct Data from API
def get_correct_race():
    while True:
        try: 
            country = input("Which Grand Prix would you like to see? (e.g. Australia, Monaco, etc.) ")
            year = input("Which year would you like to see? (e.g. 2025) ")
            session_type = input("Which session would you like to see? (e.g. Qualifying, Race, etc.) ")    
        except EOFError:
            print("Input Error: Unexpected end of input. Please try again.")
            break

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
                continue 
            
            # print(data)
            session = data[0] # As this only returns one session, we know it will be the first in the list.
            session_key = session['session_key']
            print(f"\nFound: {session['country_name']} {session['year']} — {session['session_type']} | Session Key: {session_key}")
            return session_key

        except requests.exceptions.ConnectionError:
            print("Network error: Unable to connect to the API. Please check your internet connection and try again.")
        except requests.exceptions.HTTPError:
            print(f"HTTP error: {response.status_code} - {response.reason}. Please check your input and try again.")
            print("Make sure to input the country name, year, and session type correctly (e.g. Australia, 2025, Qualifying).")
        except Exception as e:
            print(f"An error occurred: {e}. Please try again.")


def get_drivers_info(session_key):
    try:
        response = requests.get(f"https://api.openf1.org/v1/drivers?session_key={session_key}")
        response.raise_for_status() # Raise HTTP error - only really a safeguard.  
        driver_info = response.json()

        drivers = []

        for driver in driver_info:
            drivers.append({
                "driver_number": driver.get("driver_number"),
                "name": driver.get("full_name"),
                "team_colour": f"#{driver.get('team_colour')}" # API returns hex without #
            })
        # print(drivers)
        return drivers

    except requests.exceptions.HTTPError:
        print(f"HTTP error fetching drivers: {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"Error Fetching drivers: {e}")


def get_lap_times(session_key, drivers):
    lap_data = {}

    for driver in drivers:
        driver_number = driver["driver_number"] 

        try: 
            response = requests.get(
                "https://api.openf1.org/v1/laps",
                params={
                    "session_key": session_key,
                    "driver_number": driver_number,
                    }
            )
            response.raise_for_status()
            laps = response.json() 

            lap_times = []
            for lap in laps:
                time = lap.get("lap_duration")
                lap_times.append(time)

            # This extracts the lap duration for each lap, preserving the lap order
            # Some laps may have None (e.g. Pit Laps or Safety) - but we keep them so that lap_number still maps to the correct index later. 
            # Also using the .get() function is safer if it does not return correct Key. 
            # lap_times = [lap.get("lap_duration") for lap in laps] ~ could have used this instead. 

            lap_data[driver_number] = {
                "name": driver["name"],
                "lap_times": lap_times,
            }
            # Will attempt to use the driver_numbers as a key as this is what the API uses to filter parameter and is unique to per drivers
        
        except Exception as e:
            print(f"Error for driver {driver_number}: {e}")
    
    return lap_data
    # Seeing Data: 
    # print(lap_data)

def visualise_data(drivers, lap_data): 
    fig = go.Figure()

    colour_map = {d["driver_number"]: d["team_colour"] for d in drivers}

    for driver_number, info in lap_data.items():
        colour = colour_map.get(driver_number, "#FFFFFF")

        valid_laps = [
            (i + 1, t)
            for i, t in enumerate(info["lap_times"])
            if t is not None
        ]

        if not valid_laps:
            continue

        x_laps, y_times = zip(*valid_laps)

        fig.add_trace(go.Scatter(
            x=list(x_laps),
            y=list(y_times),
            mode="lines+markers",
            name=info["name"],
            line=dict(color=colour, width=2),
            marker=dict(size=4),
            hovertemplate=(
                f"<b>{info['name']}</b><br>"
                "Lap %{x}<br>"
                "Time: %{y:.3f}s<br>"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title="Lap Times for Each Driver",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (seconds)",
        legend_title="Drivers",
        hovermode="closest",
        template="plotly_dark"
    )

    fig.show()


# -- Main -- 
def main():
    SESSION_KEY = get_correct_race()
    if SESSION_KEY is None:
        print("No valid session key was obtained. Exiting the program.")
        return

    DRIVERS = get_drivers_info(SESSION_KEY)
    if DRIVERS is None:
        print("No driver information was obtained. Exiting the program.")
        return
    
    LAP_TIMES = get_lap_times(SESSION_KEY, DRIVERS)
    visualise_data(DRIVERS, LAP_TIMES)

if __name__ == "__main__":
    main()

