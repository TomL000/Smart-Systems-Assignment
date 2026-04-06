import sqlite3
import random
import time

humidityThresholdHigh = 70
humidityThresholdLow = 35

def genHumidity():
    return round (random.uniform(30, 80), 2)

sqlConnection = sqlite3.connect("humidity.db")
sqlCursor = sqlConnection.cursor()

sqlCursor.execute(
"""CREATE TABLE IF NOT EXISTS humidity_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    humidity REAL
    )"""
)

while True:
    humidity = genHumidity()

    sqlCursor.execute("INSERT INTO humidity_reading (humidity) VALUES (?)", (humidity,))
    sqlConnection.commit()

    print (f"[LIVE] Recorded humidity: {humidity}%")
    if humidity > humidityThresholdHigh:
        print(f"WARNING High Humidity Alert: {humidity}%")
    elif humidity < humidityThresholdLow:
        print(f"WARNING Low Humidity Alert: {humidity}%")
    time.sleep(2)

sqlCursor.execute("SELECT * FROM humidity readings")
sqlRows = sqlCursor.fetchall()

for row in sqlRows:
    print(row)

sqlConnection.close()
