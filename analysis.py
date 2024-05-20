import f1_analysis, fastf1

#drivers = ["VER","NOR","LEC","PIA","SAI","HAM","RUS","PER","STR","TSU"]
drivers=["VER","NOR","LEC","HAM"]
r="race"

# Plot telemetry with turns
f1_analysis.plot_telemetry_with_turns([f1_analysis.get_driver_telemetry(2024, 'Imola', r, driver) for driver in drivers], 
                                      [d for d in drivers])

# Plot additional data
#race = fastf1.get_session(2024, 'China', 'race')
#ace.load()
#f1_analysis.plot_additional_data(race)