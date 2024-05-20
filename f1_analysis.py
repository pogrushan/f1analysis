"""
f1_analysis.py

A library for analyzing Formula 1 telemetry and race data using the FastF1 library.

Functions:
- get_driver_telemetry(year, gp, session, driver_code): Retrieve telemetry data for a specific driver from a given GP session.
- find_turns(telemetry, speed_threshold=100, brake_threshold=50): Find turns based on significant changes in speed and brake data.
- plot_telemetry_with_turns(telemetries, drivers): Plot telemetry data with turn annotations.
- plot_additional_data(session): Plot tire degradation, weather, track temperature, and humidity.

Example usage:
    import f1_analysis

    # Retrieve telemetry for two drivers
    tel1 = f1_analysis.get_driver_telemetry(2024, 'Imola', 'fp2', 'LEC')
    tel2 = f1_analysis.get_driver_telemetry(2024, 'Imola', 'fp2', 'SAI')

    # Plot telemetry with turns
    f1_analysis.plot_telemetry_with_turns([tel1, tel2], ['LEC', 'SAI'])

    # Plot additional data
    race = fastf1.get_session(2024, 'Imola', 'race')
    race.load()
    f1_analysis.plot_additional_data(race)
"""

import fastf1
import matplotlib.pyplot as plt
import numpy as np

# Enable caching
fastf1.Cache.enable_cache('./cache')

# Function to retrieve telemetry data for a specific driver from a given GP session
def get_driver_telemetry(year, gp, session, driver_code):
    """
    Retrieve telemetry data for a specific driver from a given GP session.

    Parameters:
    year (int): Year of the GP
    gp (str): Name of the GP (e.g., 'Imola')
    session (str): Session type (e.g., 'fp2', 'qualifying', 'race')
    driver_code (str): Driver code (e.g., 'LEC' for Leclerc)

    Returns:
    pandas.DataFrame: Telemetry data of the driver
    """
    session_data = fastf1.get_session(year, gp, session)
    session_data.load()
    laps = session_data.laps
    driver_fastest_lap = laps.pick_driver(driver_code).pick_fastest()
    telemetry = driver_fastest_lap.get_telemetry()
    return telemetry

# Function to find turns based on significant changes in speed and brake data
def find_turns(telemetry, speed_threshold=100, brake_threshold=50):
    """
    Find turns based on significant changes in speed and brake data.

    Parameters:
    telemetry (pandas.DataFrame): Telemetry data
    speed_threshold (float): Speed threshold to detect deceleration (default=100 km/h)
    brake_threshold (float): Brake threshold to detect braking (default=50%)

    Returns:
    list: List of distances where turns are detected
    """
    turns = []
    speed = telemetry['Speed']
    brake = telemetry['Brake']

    # Detect significant braking events
    brake_events = np.where(brake > brake_threshold)[0]

    # Find start of braking zones
    for event in brake_events:
        if speed.iloc[event] < speed_threshold and event not in turns:
            turns.append(telemetry['Distance'].iloc[event])

    return turns

# Function to plot telemetry data with turn annotations
def plot_telemetry_with_turns(telemetries, drivers):
    """
    Plot telemetry data with turn annotations.

    Parameters:
    telemetries (list): List of telemetry data frames to plot
    drivers (list): List of driver codes corresponding to the telemetries
    """
    fig, ax = plt.subplots(6, 1, figsize=(12, 25), sharex=True)
    plt.style.use('dark_background')
    colors = ['orange', 'red', 'blue', 'green', 'pink', "grey", "black", "yellow", "brown"]  # Add more colors if needed

    for i, telemetry in enumerate(telemetries):
        driver = drivers[i]
        color = colors[i % len(colors)]
        
        turns = find_turns(telemetry)
        
        ax[0].plot(telemetry['Distance'], telemetry['Speed'], label=f'{driver} - Speed', color=color)
        ax[1].plot(telemetry['Distance'], telemetry['Throttle'], label=f'{driver} - Throttle', color=color)
        ax[2].plot(telemetry['Distance'], telemetry['Brake'], label=f'{driver} - Brake', color=color)
        ax[3].plot(telemetry['Distance'], telemetry['RPM'], label=f'{driver} - RPM', color=color)
        ax[4].plot(telemetry['Distance'], telemetry['nGear'], label=f'{driver} - Gear', color=color)
        ax[5].plot(telemetry['Distance'], telemetry['DRS'], label=f'{driver} - DRS', color=color)

        for a in ax:
            for turn in turns:
                a.axvline(x=turn, color='gray', linestyle='--')
                a.annotate(f'Turn {turns.index(turn) + 1}', xy=(turn, a.get_ylim()[1]), xytext=(turn, a.get_ylim()[1] + 10),
                           textcoords='data', arrowprops=dict(facecolor='black', shrink=0.05))

    ax[0].set_ylabel('Speed (km/h)')
    ax[1].set_ylabel('Throttle (%)')
    ax[2].set_ylabel('Brake (%)')
    ax[3].set_ylabel('RPM')
    ax[4].set_ylabel('Gear')
    ax[5].set_ylabel('DRS')
    ax[5].set_xlabel('Distance (m)')

    for a in ax:
        a.legend()

    plt.tight_layout()
    # Subplot adjustment tool
    plt.subplots_adjust(left=0.06, bottom=0.043, right=0.988, top=0.994, wspace=0.2, hspace=0.042)
    plt.show()

def plot_additional_data(session, selected_drivers=None):
    """
    Plot tire degradation, weather, track temperature, and humidity.

    Parameters:
    session (Session): Loaded session from fastf1
    selected_drivers (list or None): List of driver codes to plot data for. If None, plot data for all drivers.
    """
    weather_data = session.weather_data
    tire_data = session.laps[['LapNumber', 'Compound', 'TyreLife', 'Driver']]

    if selected_drivers is not None:
        tire_data = tire_data[tire_data['Driver'].isin(selected_drivers)]

    fig, ax = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    # Weather plot
    ax[0].plot(weather_data['Time'], weather_data['AirTemp'], label='Air Temp (°C)', color='blue')
    ax[0].plot(weather_data['Time'], weather_data['TrackTemp'], label='Track Temp (°C)', color='red')
    ax[0].plot(weather_data['Time'], weather_data['Humidity'], label='Humidity (%)', color='green')
    ax[0].set_ylabel('Temperature / Humidity')
    ax[0].legend()

    # Tyre degradation plot
    markers = ['o', 's', '^', 'd']  # Marker styles for different drivers
    for i, driver in enumerate(tire_data['Driver'].unique()):
        driver_data = tire_data[tire_data['Driver'] == driver]
        for j, compound in enumerate(driver_data['Compound'].unique()):
            compound_data = driver_data[driver_data['Compound'] == compound]
            ax[1].plot(compound_data['LapNumber'], compound_data['TyreLife'],
                       label=f'{driver} - {compound}', marker=markers[j % len(markers)], linestyle='-')
    
    ax[1].set_ylabel('Tyre Life (laps)')
    ax[1].set_xlabel('Lap Number')
    ax[1].legend()

    plt.tight_layout()
    # Subplot adjustment tool
    plt.subplots_adjust(left=0.06, bottom=0.038, right=0.988, top=0.994, wspace=0.2, hspace=0.042)
    plt.show()