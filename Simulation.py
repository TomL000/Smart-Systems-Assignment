import sqlite3
import random
import time
import math
from datetime import datetime

# Thresholds for a high and low temperatures

humidityThresholdHigh = 70
humidityThresholdLow = 35

zones = {
    "zone1_propagation": (85, 95),
    "zone2_vegetation": (60, 75),
    "zone3_flowering": (45, 60),
    "zone4_storage": (90, 95)
}

# Defines a humidity generator
##H# set zone as a parameter
def genHumidity(zone):
    timeNow = datetime.now().hour

    smallVariation = 3 * math.sin((timeNow / 24) * 2 * math.pi)

    # simulated humidity per zone
    if zone == "zone1_propagation":
        base = random.uniform(85, 95)

    elif zone == "zone2_vegetation":
        base = random.uniform(60, 75)

    elif zone == "zone3_flowering":
        base = random.uniform(45, 60)

    elif zone == "zone4_storage":
        base = random.uniform(90, 95)

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
    #connection to sql database
    sqlConnection = sqlite3.connect("humidity.db")
    sqlCursor = sqlConnection.cursor()
    try:
        while True:
            readings = {}
            for zone in zones:
                humidity = genHumidity(zone)
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
