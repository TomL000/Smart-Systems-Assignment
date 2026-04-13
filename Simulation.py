import sqlite3
import random
import time
import math
import json ##H# for zone.json integration
from datetime import datetime

# Thresholds for a high and low temperatures

humidityThresholdHigh = 70
humidityThresholdLow = 35


# Defines a humidity generator
##H# set zone, low & high values as parameters
def genHumidity(zone, low, high):
    timeNow = datetime.now().hour
    smallVariation = 3 * math.sin((timeNow / 24) * 2 * math.pi)
    base = random.uniform(low, high) ##H#uses zone.json profile instead of hardcoded value
    humidity = base + smallVariation + random.uniform(-2, 2)

    # Rare weather spike
    if random.random() < 0.03: # this is a 3% chance of happening
        temperatureSpike = random.choice([-15, 15])
        humidity += temperatureSpike
        print("There has been a spike in the temperature!")

    # Realistic humidity boundaries
    humidity = max(20, min(100, humidity))

    return round (humidity, 2)

# Sql cursor to insert a table into the SQL database that stores the humidity readings.
##H# ~bugfix~ Deleted, zone creation is handled in main

print (" Starting multi-zone monitoring program")
# Live while loop that executes the humidity readings and compares them into the threshholds
##H# wrapping while loop into a function to be called in main.py
def run():

    #H# loads simulation profiles from zones.json
    with open("zones.json", "r") as file:
        data = json.load(file)

    #build zones dictionary from zones.json
    zones = {f"zone{z['zoneNum']}_{z['zoneName']}": (int(z["minHumidity"]), int(z["maxHumidity"])) for z in data["zones"]}
    #H#

    #connection to sql database
    sqlConnection = sqlite3.connect("humidity.db")
    sqlCursor = sqlConnection.cursor()
    print("Starting multi-zone monitoring simulation")
    try:
        while True:
            readings = {}
            for zone in zones:
                humidity = genHumidity(zone, zones[zone][0], zones[zone][1]) ##H# set low and high values for each zone
                readings[zone] = humidity

                sqlCursor.execute(f"INSERT INTO {zone} (humidity) VALUES (?)", (humidity,))
                sqlConnection.commit()

            print (f"[{datetime.now().strftime('%H:%M:%S')}]")
            for zone, humidity in readings.items():
                print(f"[LIVE] Recorded humidity: {humidity}% -> {zone}")

            # Alerts ("h" is just another humidity variable im not naming currently)
            for zone, (low, high) in zones.items():
                h = readings[zone]

                if h < low:
                    print(f"{zone} is too dry!")
                elif h > high:
                    print(f"{zone} is too dry!")

            time.sleep(10)

    except KeyboardInterrupt:
        print("Stopping monitoring...")

        # Show last 5 entries from each zone
        #H# ~bugfix~ removed non-existant articles causing crashes
        for zone in list(zones.keys()):
            print(f"\n--- {zone} ---")
            sqlCursor.execute(f"SELECT * FROM {zone} ORDER BY id DESC LIMIT 5")
            rows = sqlCursor.fetchall()
            for row in rows:
                print(row)

        sqlConnection.close()
