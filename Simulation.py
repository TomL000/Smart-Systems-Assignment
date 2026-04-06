import sqlite3
import random
import time

# Thresholds for a high and low temperatures

humidityThresholdHigh = 70
humidityThresholdLow = 35
 
# Defines a humidity generator

def genHumidity():
    return round (random.uniform(30, 80), 2)

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

# Live while loop that executes the humidity readings and compares them into the threshholds

while True:
    humidity = genHumidity()

    sqlCursor.execute("INSERT INTO humidity_readings (humidity) VALUES (?)", (humidity,))
    sqlConnection.commit()

    print (f"[LIVE] Recorded humidity: {humidity}%")
    if humidity > humidityThresholdHigh:
        print(f"WARNING High Humidity Alert: {humidity}%")
    elif humidity < humidityThresholdLow:
        print(f"WARNING Low Humidity Alert: {humidity}%")
    time.sleep(30)

# fetches from the sql table and prints in a row from this file.
sqlCursor.execute("SELECT * FROM humidity readings")
sqlRows = sqlCursor.fetchall()

for row in sqlRows:
    print(row)

sqlConnection.close()
