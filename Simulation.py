import sqlite3
import random
import time
import math
from datetime import datetime

# Thresholds for a high and low temperatures

humidityThresholdHigh = 70
humidityThresholdLow = 35
 
# Defines a humidity generator

def genHumidity():
    timeNow = datetime.now()
    hourNow = timeNow.hour

    base = 55 + 15 * math.sin((hourNow / 24) * 2 * math.pi - math.pi/2)
    temperatureSpike = random.choice([-10, -5, 0, 5,10])
    noise = random.uniform(-3, 3)
    
    humidity = base + temperatureSpike + noise

    if random.random() < 0.05: # this is a 5% chance of happening
        temperatureSpike = random.choice([-20, 20])
        humidity += temperatureSpike
        print("There has been a spike in the temperature!")

    humidity = max(20, min(90, humidity))

    return round (humidity, 2)

# Connection to sql database

sqlConnection = sqlite3.connect("humidity.db")
sqlCursor = sqlConnection.cursor()

# Sql cursor to insert a table into the SQL database that stores the humidity readings.

sqlCursor.execute(
"""CREATE TABLE IF NOT EXISTS humidity_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    humidity REAL
    )"""
)

print (" Starting monitoring program")
# Live while loop that executes the humidity readings and compares them into the threshholds
try:
    while True:
        humidity = genHumidity()

        sqlCursor.execute("INSERT INTO humidity_readings (humidity) VALUES (?)", (humidity,))
        sqlConnection.commit()

        print (f"[{datetime.now().strftime('%H:%M:%S')}] [LIVE] Recorded humidity: {humidity}%")

        # Alerts
        if humidity > humidityThresholdHigh:
            print(f"WARNING High Humidity Alert: {humidity}%")
        elif humidity < humidityThresholdLow:
            print(f"WARNING Low Humidity Alert: {humidity}%")
        time.sleep(30)

except KeyboardInterrupt:
    print("Stopping monitoring...")

    sqlCursor.execute("SELECT * FROM humidity_readings")
    rows = sqlCursor.fetchall()

    print("Stored readings:")
    for now in rows[-10:]: 
        print(rows)

    sqlConnection.close()
